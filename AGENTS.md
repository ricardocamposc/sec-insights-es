# AGENTS.md

Guía para agentes que trabajen en SEC Insights, contrastada con el código, los
manifiestos y los comandos existentes en este proyecto.

## Contexto del proyecto

SEC Insights es una aplicación full-stack RAG para consultar documentos
financieros SEC (10-K/10-Q). El frontend permite seleccionar documentos y
mantiene una conversación; el backend combina índices PGVector con datos
cuantitativos de Polygon.io y transmite la respuesta mediante SSE.

La estructura confirmada es:

- `frontend/`: Next.js 13, React 18, TypeScript y Tailwind CSS.
- `backend/`: FastAPI, Python 3.11, Poetry, SQLAlchemy async, LlamaIndex y
  PostgreSQL/PGVector.

## Comandos de desarrollo

Ejecuta los comandos desde el directorio indicado.

### Backend

Desde `backend/`:

```bash
poetry install
cp .env.development .env
set -a && source .env
make migrate
make run
```

`make run` crea e inicia los servicios `db`, `localstack` y `phoenix` con
Docker Compose y arranca FastAPI en el host. El backend escucha en
`http://localhost:8000`.

Otros comandos disponibles:

```bash
make test                    # poetry run python -m pytest tests/
poetry run python -m pytest tests/app/chat/test_engine.py
make chat                    # REPL contra http://localhost:8000
make seed_db_local           # Amazon y Meta 10-K en DB/LocalStack local
make refresh_db              # pide confirmación y borra la DB local
```

No documentar `make chat_prod`: ese target no existe actualmente en
`backend/Makefile`. Para sembrar datos, `make seed_db_local` ejecuta
`python scripts/seed_db.py` directamente, por lo que conviene tener activa la
virtualenv de Poetry; los demás targets usan `poetry run` explícitamente.

`make run`, `make migrate` y `make seed_db_local` necesitan Docker en ejecución.
La aplicación necesita que exista `backend/.env`; el repositorio solo incluye
la plantilla `backend/.env.development`.

### Frontend

Desde `frontend/`:

```bash
npm i
npm run dev
npm run build
npm run lint
```

El frontend requiere `NEXT_PUBLIC_BACKEND_URL`. La validación de variables se
define en `frontend/src/env.mjs`; `SKIP_ENV_VALIDATION=1` permite saltarla en
builds de Docker.

## Arquitectura confirmada

### Backend

- `app/api/` registra `/api/conversation`, `/api/document` y `/api/health`.
- `app/api/endpoints/conversation.py` devuelve `EventSourceResponse` para el
  chat.
- `app/chat/engine.py` construye un `OpenAIAgent` con dos
  `SubQuestionQueryEngine`: uno cualitativo sobre índices PGVector y otro
  cuantitativo que usa Polygon.io.
- `app/chat/messaging.py` coordina el streaming y publica tokens y eventos de
  `MessageSubProcess`.
- `app/chat/qa_response_synth.py` contiene los prompts de síntesis de
  respuestas SEC; `app/chat/constants.py` contiene el mensaje de sistema.
- `app/chat/pg_vector.py` implementa el singleton `CustomPGVectorStore` sobre
  PostgreSQL/PGVector.
- `app/models/db.py` define `Document`, `Conversation`,
  `ConversationDocument`, `Message` y `MessageSubProcess`, con UUID como clave
  primaria.
- `app/chat/engine.py` descarga PDFs desde S3/LocalStack, los procesa con
  `PDFReader`, crea un `VectorStoreIndex` y persiste el contexto en S3; las
  cargas posteriores usan el contexto cacheado.
- En entorno no-Render se configura el handler local de Arize Phoenix; la
  URL esperada para el panel local es `http://localhost:6006`.

### Frontend

- `/` está implementada en `src/pages/index.tsx` y combina `SelectTicker` con
  la sección de marketing.
- `/conversation/[id]` está implementada en
  `src/pages/conversation/[id].tsx`; muestra conversación a la izquierda y
  PDFs a la derecha.
- `useMessages.tsx` consume SSE y procesa mensajes y subprocesos.
- `useDocumentSelector.tsx` mantiene la selección de documentos.
- `usePdfViewer.tsx` y `useMultiplePdfs.tsx` gestionan foco, scroll y
  múltiples PDFs.
- `VirtualizedPdf.tsx` usa `react-pdf` y `react-window`; `DisplayMultiplePdfs`
  coordina la visualización de varios documentos.
- `src/api/backend.tsx` centraliza las peticiones y construye sus URLs desde
  `NEXT_PUBLIC_BACKEND_URL`.

## Variables de entorno

Backend: `OPENAI_API_KEY`, `DATABASE_URL`, `S3_ASSET_BUCKET_NAME`, `AWS_KEY`,
`AWS_SECRET`, `POLYGON_IO_API_KEY`, `SEC_EDGAR_COMPANY_NAME` y
`SEC_EDGAR_EMAIL`. También se usan `S3_BUCKET_NAME`, `CDN_BASE_URL`, CORS y las
variables de Render/observabilidad definidas en `app/core/config.py`.

Frontend: `NEXT_PUBLIC_BACKEND_URL` (y, opcionalmente, variables de Codespaces
definidas en `frontend/src/env.mjs`). Nunca commits credenciales reales ni
reemplaces los placeholders del archivo de plantilla con secretos.

## Adaptar a documentos no SEC

Actualiza conjuntamente los puntos que están acoplados al dominio SEC:

- mensaje de sistema: `backend/app/chat/constants.py`;
- prompts de síntesis: `backend/app/chat/qa_response_synth.py`;
- descripciones de herramientas de `get_chat_engine()` en
  `backend/app/chat/engine.py`;
- prefijo del mensaje de usuario en `backend/app/chat/messaging.py`.

## Verificación antes de entregar cambios

1. Ejecuta el test específico afectado y después `make test` desde `backend/`.
2. Ejecuta `npm run lint` y `npm run build` desde `frontend/`.
3. Si cambias migraciones, API, configuración o integración con servicios,
   verifica el flujo local con Docker, `make migrate` y `make run` cuando haya
   credenciales y variables configuradas.
4. No declares que una verificación pasó si el entorno no tiene dependencias,
   servicios o credenciales; reporta el comando y el motivo del bloqueo.

## Estado de esta verificación

Confirmado mediante inspección del código y configuración:

- `backend/pyproject.toml` fija Python `^3.11,<3.12` y `poetry check` pasa.
- Los targets `run`, `migrate`, `test`, `chat`, `seed_db_local` y
  `refresh_db` existen en `backend/Makefile`.
- Las rutas, componentes, dependencias y mecanismos de streaming descritos
  arriba están presentes en el árbol de fuentes.
- La composición local declara PostgreSQL/PGVector, LocalStack y Phoenix.

No se ejecutaron tests ni el build real porque en el entorno de verificación no
estaban instalados `backend/.venv` ni `frontend/node_modules`. Tampoco se
arrancaron servicios porque no existe `backend/.env` y eso es requerido por
`backend/docker-compose.yml`.
