from typing import cast
import uvicorn
import logging
import sys
import sentry_sdk
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from alembic.config import Config
import alembic.config
from alembic import script
from alembic.runtime import migration
from sqlalchemy.engine import create_engine, Engine
from llama_index.core.node_parser.text.utils import split_by_sentence_tokenizer
import llama_index.core

from app.api.api import api_router
from app.db.wait_for_db import check_database_connection
from app.db.session import engine as async_engine
from app.core.config import settings, AppEnvironment
from app.loader_io import loader_io_router
from contextlib import asynccontextmanager
import asyncio
import copy
import dataclasses
import gc
from app.chat.pg_vector import get_vector_store_singleton, CustomPGVectorStore
from app.chat.engine import close_s3_resources
from app.llama_index_settings import _setup_llama_index_settings

logger = logging.getLogger(__name__)


def __setup_phoenix() -> None:
    """Enable Phoenix without deepcopying live asyncio loops.

    The pinned OpenInference integration serializes callback payloads with
    ``copy.deepcopy``. Some payloads contain an event loop owned by an async
    client; deepcopy creates an uninitialized loop whose destructor later
    emits ``BaseEventLoop.__del__`` errors. Event loops are implementation
    details, not useful trace data, so represent them as text during encoding.
    """
    from openinference.instrumentation.llama_index import _handler

    def safe_asdict(obj):
        if dataclasses.is_dataclass(obj):
            return {
                field.name: safe_asdict(getattr(obj, field.name))
                for field in dataclasses.fields(obj)
            }
        if isinstance(obj, tuple) and hasattr(obj, "_fields"):
            return type(obj)(*(safe_asdict(value) for value in obj))
        if isinstance(obj, (list, tuple)):
            return type(obj)(safe_asdict(value) for value in obj)
        if isinstance(obj, dict):
            return type(obj)(
                (safe_asdict(key), safe_asdict(value)) for key, value in obj.items()
            )
        if _handler._show_repr_str(obj):
            return _handler._show_repr_str(obj)
        if isinstance(obj, asyncio.AbstractEventLoop):
            return repr(obj)

        memo = {
            id(loop): repr(loop)
            for loop in gc.get_objects()
            if isinstance(loop, asyncio.AbstractEventLoop)
        }
        try:
            return copy.deepcopy(obj, memo)
        except BaseException:
            return repr(obj)

    _handler._asdict = safe_asdict
    llama_index.core.set_global_handler("arize_phoenix")


def check_current_head(alembic_cfg: Config, connectable: Engine) -> bool:
    directory = script.ScriptDirectory.from_config(alembic_cfg)
    with connectable.begin() as connection:
        context = migration.MigrationContext.configure(connection)
        return set(context.get_current_heads()) == set(directory.get_heads())


def __setup_logging(log_level: str):
    log_level = getattr(logging, log_level.upper())
    log_formatter = logging.Formatter(
        "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
    )
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(log_formatter)
    root_logger.addHandler(stream_handler)
    logger.info("Set up logging with log level %s", log_level)


def __setup_sentry():
    if settings.SENTRY_DSN:
        logger.info("Setting up Sentry")
        if settings.ENVIRONMENT == AppEnvironment.PRODUCTION:
            profiles_sample_rate = None
        else:
            profiles_sample_rate = settings.SENTRY_SAMPLE_RATE
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.ENVIRONMENT.value,
            release=settings.RENDER_GIT_COMMIT,
            debug=settings.VERBOSE,
            traces_sample_rate=settings.SENTRY_SAMPLE_RATE,
            profiles_sample_rate=profiles_sample_rate,
        )
    else:
        logger.info("Skipping Sentry setup")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # first wait for DB to be connectable
    await check_database_connection()
    cfg = Config("alembic.ini")
    # Change DB URL to use psycopg2 driver for this specific check
    db_url = settings.DATABASE_URL.replace(
        "postgresql+asyncpg://", "postgresql+psycopg2://"
    )
    cfg.set_main_option("sqlalchemy.url", db_url)
    engine = create_engine(db_url, echo=True)
    try:
        if not check_current_head(cfg, engine):
            raise Exception(
                "Database is not up to date. Please run `poetry run alembic upgrade head`"
            )
    finally:
        engine.dispose()
    # initialize pg vector store singleton
    vector_store = await get_vector_store_singleton()
    vector_store = cast(CustomPGVectorStore, vector_store)
    await vector_store.run_setup()

    try:
        # Some setup is required to initialize the llama-index sentence splitter
        split_by_sentence_tokenizer()
    except FileExistsError:
        # Sometimes seen in deployments, should be benign.
        logger.info("Tried to re-download NLTK files but already exists.")

    if not settings.RENDER and settings.ENABLE_PHOENIX:
        __setup_phoenix()

    yield
    # This section is run on app shutdown
    await vector_store.close()
    await async_engine.dispose()
    close_s3_resources()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    lifespan=lifespan,
)


if settings.BACKEND_CORS_ORIGINS:
    origins = settings.BACKEND_CORS_ORIGINS.copy()
    if settings.CODESPACES and settings.CODESPACE_NAME and \
        settings.ENVIRONMENT == AppEnvironment.LOCAL:
        # add codespace origin if running in Github codespace
        origins.append(f"https://{settings.CODESPACE_NAME}-3000.app.github.dev")
    # allow all origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin).rstrip("/") for origin in origins],
        allow_origin_regex="https://llama-app-frontend.*\.vercel\.app",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_PREFIX)
app.mount(f"/{settings.LOADER_IO_VERIFICATION_STR}", loader_io_router)


def start():
    print("Running in AppEnvironment: " + settings.ENVIRONMENT.value)
    __setup_logging(settings.LOG_LEVEL)
    __setup_sentry()
    _setup_llama_index_settings()
    """Launched with `poetry run start` at root level"""
    if settings.RENDER:
        # on render.com deployments, run migrations
        logger.debug("Running migrations")
        alembic_args = ["--raiseerr", "upgrade", "head"]
        alembic.config.main(argv=alembic_args)
        logger.debug("Migrations complete")
    else:
        logger.debug("Skipping migrations")
    live_reload = not settings.RENDER
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=live_reload,
        workers=settings.UVICORN_WORKER_COUNT,
    )
