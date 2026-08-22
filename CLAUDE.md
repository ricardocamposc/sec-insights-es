# CLAUDE.md

Este archivo proporciona orientación a Claude Code (claude.ai/code) cuando trabaja con el código de este repositorio.

## Descripción general

SEC Insights es una aplicación RAG full-stack para analizar documentos financieros de la SEC. Los usuarios seleccionan documentos (formularios 10-K/10-Q) y conversan con una IA que responde preguntas consultando un almacén PGVector y la API de datos financieros de Polygon.io.

## Estructura del repositorio

- `frontend/` — Aplicación Next.js 13 (TypeScript, Tailwind CSS)
- `backend/` — Aplicación FastAPI (Python 3.11, Poetry, LlamaIndex, SQLAlchemy async)

## Comandos del backend

Todos los comandos se ejecutan desde `backend/`. Requiere un shell de Poetry activo (`poetry shell`).

```bash
make run              # Inicia el servidor + contenedores Docker (DB, Localstack, Arize Phoenix)
make migrate          # Ejecuta migraciones de Alembic + construye tablas PGVector
make test             # Ejecuta tests: poetry run python -m pytest tests/
make chat             # REPL de shell para probar el chat contra el servidor local
make seed_db_local    # Poblar la DB local con docs 10-K de AMZN y META via Localstack
make refresh_db       # Borra la DB local y vuelve a ejecutar las migraciones
```

Configuración del entorno:
```bash
cp .env.development .env
set -a && source .env
```

Ejecutar un solo test:
```bash
poetry run python -m pytest tests/app/chat/test_engine.py
```

## Comandos del frontend

Todos los comandos se ejecutan desde `frontend/`.

```bash
npm i          # Instalar dependencias
npm run dev    # Iniciar servidor de desarrollo
npm run build  # Build + verificación de tipos TypeScript
npm run lint   # ESLint
```

## Arquitectura del backend

**Capa API** (`app/api/`): Tres routers — `/api/conversation`, `/api/document`, `/api/health`. Las respuestas del chat se transmiten via SSE.

**Pipeline de chat** (`app/chat/`):
- `engine.py` — Núcleo: construye un `OpenAIAgent` con dos herramientas `SubQuestionQueryEngine`:
  - *cualitativa*: consulta índices PGVector por documento
  - *cuantitativa*: llama a la API de Polygon.io para métricas financieras
- `messaging.py` — `handle_chat_message` gestiona el streaming; `ChatCallbackHandler` intercepta eventos de callback de LlamaIndex y transmite actualizaciones de `MessageSubProcess` al cliente junto con los tokens de respuesta
- `qa_response_synth.py` — Sintetizador de respuestas personalizado con prompts específicos para la SEC
- `constants.py` — Plantilla del mensaje de sistema
- `tools.py` — Herramienta de query engine para la API de Polygon.io
- `pg_vector.py` — Singleton `CustomPGVectorStore` respaldado por PostgreSQL + pgvector

**Modelos de datos** (`app/models/db.py`): `Document`, `Conversation`, `ConversationDocument` (many-to-many), `Message`, `MessageSubProcess`. Todos extienden `Base` con PKs UUID.

**Indexación de documentos**: Los PDFs se almacenan en S3 (Localstack localmente). En el primer chat con un documento, `engine.py` descarga el PDF, lo procesa con `PDFReader` y construye un `VectorStoreIndex` que se persiste de vuelta en S3. Las cargas posteriores usan `StorageContext` con caché TTL.

**Observabilidad LLM**: Arize Phoenix corre localmente en `http://localhost:6006` y recibe todas las trazas de LlamaIndex automáticamente (deshabilitado en despliegues de Render).

## Arquitectura del frontend

**Rutas** (`src/pages/`):
- `/` (`index.tsx`) — Página de inicio: selector de documentos (`SelectTicker`) + sección de marketing
- `/conversation/[id]` — Vista dividida: panel de chat (izquierda) + visor de PDF (derecha)

**Hooks principales**:
- `useMessages.tsx` — Consume el stream SSE del backend; parsea eventos `StreamedMessage` y `MessageSubProcess`
- `useDocumentSelector.tsx` — Gestiona el estado de los documentos seleccionados
- `usePdfViewer.tsx` / `useMultiplePdfs.tsx` — Estado de scroll, resaltado y múltiples documentos PDF

**Renderizado de PDFs**: `VirtualizedPdf.tsx` usa `react-pdf` + `react-window` para renderizado virtualizado. `DisplayMultiplePdfs.tsx` orquesta múltiples PDFs en paralelo.

**Comunicación con el backend** (`src/api/backend.tsx`): Todas las llamadas a la API; usa la variable de entorno `NEXT_PUBLIC_BACKEND_URL`.

## Configuración principal

- Variables de entorno del backend: `OPENAI_API_KEY`, `DATABASE_URL`, `S3_ASSET_BUCKET_NAME`, `AWS_KEY`, `AWS_SECRET`, `POLYGON_IO_API_KEY`, `SEC_EDGAR_COMPANY_NAME`, `SEC_EDGAR_EMAIL`
- Variables de entorno del frontend: `NEXT_PUBLIC_BACKEND_URL` (definida en `.env.example`)
- La versión de Python está fijada en `^3.11,<3.12` (ver `backend/.python-version`)

## Personalización para documentos no-SEC

Para adaptar los prompts a otros tipos de documentos, modificar:
- Mensaje de sistema: `backend/app/chat/constants.py`
- Prompt del sintetizador de respuestas: `backend/app/chat/qa_response_synth.py`
- Descripciones de herramientas en `get_chat_engine()`: `backend/app/chat/engine.py` (~L254-L270)
- Prefijo del mensaje de usuario: `backend/app/chat/messaging.py` (~L143-L145)
