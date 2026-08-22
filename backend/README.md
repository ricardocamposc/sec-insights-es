# Backend de SEC Insights
Disponible en https://secinsights.ai/
## Configuración del entorno de desarrollo
Las instrucciones de comandos usan un shell compatible con Bash. En Windows
puedes ejecutarlas mediante WSL, Git Bash o adaptar los comandos a PowerShell.

1. Instala [pyenv](https://github.com/pyenv/pyenv#automatic-installer) —o una herramienta equivalente para gestionar versiones de Python— y usa la versión indicada en `.python-version`.
    * Puedes omitir este paso si usas la imagen devcontainer de GitHub Codespaces.
1. [Instala Docker](https://docs.docker.com/engine/install/) para tu sistema operativo.
    * Puedes omitir este paso si usas la imagen devcontainer de GitHub Codespaces.
1. Ejecuta `poetry shell`.
1. Ejecuta `poetry install` para instalar las dependencias del proyecto.
1. Crea el archivo `.env` y cárgalo. `.env.development` es una buena plantilla.
    1. `cp .env.development .env`
    1. `set -a`
    1. `source .env`
1. Ejecuta las migraciones de la base de datos con `make migrate`.
1. Ejecuta `make run` para iniciar el servidor localmente.
    - Esto inicia PostgreSQL 15 y LocalStack en sus propios contenedores Docker.
    - El servidor no se ejecuta en un contenedor, sino directamente en tu sistema operativo.
        - Así puedes usar herramientas de depuración como `pdb`.
1. Finalmente, probablemente querrás cargar algunos informes SEC de ejemplo en tu base de datos local.
    - Existe un script para ello. Primero, abre `.env` y sustituye el valor de ejemplo de `OPENAI_API_KEY` por tu propia clave de API de OpenAI.
        - También tendrás que hacer lo mismo con otras claves como `POLYGON_IO_API_KEY`, `AWS_KEY` y `AWS_SECRET`.
        - Para cumplir la [política de seguridad en Internet de la SEC](https://www.sec.gov/os/webmaster-faq#code-support), sustituye también `SEC_EDGAR_COMPANY_NAME` y `SEC_EDGAR_EMAIL` por tus propios valores.
    - Vuelve a cargar el archivo con `set -a` y después `source .env`.
    - Ejecuta `make seed_db_local`.
        - Si falla, puede ser útil ejecutar `make refresh_db` para limpiar la base de datos local y reiniciar las tablas vacías.
    - ¡Listo! 🏁 Ejecuta `make run` de nuevo y deberías ver documentos cargados en http://localhost:8000/api/document.

Si tienes problemas al configurar lo anterior o durante el desarrollo, puedes buscar soluciones en los siguientes lugares:
- [`backend/troubleshooting.md`](https://github.com/run-llama/sec-insights/blob/main/backend/troubleshooting.md)
- [Issues abiertos y ya cerrados de GitHub](https://github.com/run-llama/sec-insights/issues?q=is%3Aissue+is%3Aclosed)
- El [canal #sec-insights de Discord](https://discord.com/channels/1059199217496772688/1150942525968879636)

## Variables de entorno

El backend carga las variables desde `backend/.env`. Puedes crear el archivo a
partir de `.env.development`:

```bash
cp .env.development .env
```

### Variables obligatorias

Estas variables son requeridas por `app/core/config.py` para iniciar el
backend:

| Variable | Descripción | Valor local recomendado |
| --- | --- | --- |
| `DATABASE_URL` | URL de PostgreSQL. | `postgresql://user:password@127.0.0.1:${POSTGRES_PORT:-5432}/llama_app_db` si ejecutas FastAPI en el host; dentro del contenedor usa `postgresql://user:password@db:5432/llama_app_db`. |
| `OPENAI_API_KEY` | Clave de API para el LLM y embeddings. | Tu clave real de OpenAI. |
| `AWS_KEY` | Clave de acceso usada por S3/LocalStack. | `test` en local. |
| `AWS_SECRET` | Clave secreta usada por S3/LocalStack. | `test` en local. |
| `POLYGON_IO_API_KEY` | Clave para consultas financieras cuantitativas. | Tu clave real de Polygon.io. |
| `S3_BUCKET_NAME` | Bucket para los contextos e índices de LlamaIndex. | `llama-app-backend-local`. |
| `S3_ASSET_BUCKET_NAME` | Bucket para los PDF y otros assets. | `llama-app-web-assets-local`. |
| `CDN_BASE_URL` | URL desde la que se sirven los assets locales. | `http://llama-app-web-assets-local.s3-website.localhost.localstack.cloud:4566`. |

`OPENAI_API_KEY` es necesaria para que el chat funcione y
`POLYGON_IO_API_KEY` para las consultas cuantitativas. No introduzcas claves
reales en archivos versionados.

### Variables recomendadas

```env
BACKEND_CORS_ORIGINS='["http://localhost:3000","http://127.0.0.1:3000","http://localhost:8000","http://127.0.0.1:8000"]'
LOG_LEVEL=DEBUG
RENDER=False
SEC_EDGAR_COMPANY_NAME=NombreDeTuOrganizacion
SEC_EDGAR_EMAIL=tu-email@dominio.com
```

`SEC_EDGAR_COMPANY_NAME` y `SEC_EDGAR_EMAIL` identifican al cliente ante la
SEC cuando se descargan informes. Usa un nombre y un email válidos.

### Variables opcionales

Si no se definen, el backend usa estos valores predeterminados:

| Variable | Predeterminado | Uso |
| --- | --- | --- |
| `PROJECT_NAME` | `llama_app` | Nombre de la aplicación FastAPI. |
| `API_PREFIX` | `/api` | Prefijo de las rutas de la API. |
| `VECTOR_STORE_TABLE_NAME` | `pg_vector_store` | Tabla de vectores en PostgreSQL. |
| `OPENAI_CHAT_LLM_NAME` | `gpt-4o-mini` | Modelo utilizado para el chat. |
| `SENTRY_DSN` | vacío | Activa Sentry si se define. |
| `RENDER_GIT_COMMIT` | vacío | Release enviado a Sentry. |
| `LOADER_IO_VERIFICATION_STR` | valor incluido en `config.py` | Ruta de verificación de Loader.io. |
| `IS_PULL_REQUEST` | `False` | Identifica previews de pull requests en Render. |
| `CODESPACES` | `False` | Activa ajustes específicos de GitHub Codespaces. |
| `CODESPACE_NAME` | vacío | Nombre del Codespace. |

`IS_PREVIEW_ENV` también puede definirse en Render para activar la configuración
de preview; no es necesaria en local.

### Variables de Docker Compose

Estas variables configuran el nombre del proyecto y el puerto de PostgreSQL
publicado en el host:

| Variable | Predeterminado | Uso |
| --- | --- | --- |
| `COMPOSE_PROJECT_NAME` | `sec-insights-es` | Nombre que Docker Compose utiliza para los servicios, la red y los volúmenes del proyecto. |
| `POSTGRES_PORT` | `5432` | Puerto del host que se conecta al puerto interno `5432` de PostgreSQL. |

Puedes cambiar `POSTGRES_PORT` en `backend/.env` si el puerto `5432` ya está
ocupado. `DATABASE_URL` en `.env.development` usa esta variable, por lo que la
conexión del backend ejecutado en el host se actualiza automáticamente:

```env
COMPOSE_PROJECT_NAME=sec-insights-es
POSTGRES_PORT=5433
DATABASE_URL=postgresql://user:password@127.0.0.1:${POSTGRES_PORT:-5432}/llama_app_db
```

Si `POSTGRES_PORT` no está definido, Docker Compose y `DATABASE_URL` utilizan
`5432`. La URL de `.env.docker` conserva `db:5432`, porque los contenedores se
conectan mediante la red interna y PostgreSQL siempre escucha en ese puerto.

### Variables específicas de Docker

`backend/.env.docker` redefine `DATABASE_URL` con el hostname interno `db`.
No uses ese valor cuando ejecutes el backend directamente en el host.

La imagen actual `localstack/localstack:latest` puede requerir también
`LOCALSTACK_AUTH_TOKEN` en el entorno de Docker. Esta variable la consume
LocalStack, no FastAPI, y debe contener un token válido si la imagen lo exige.

`LOCALSTACK_AUTH_TOKEN` no es un valor aleatorio ni una contraseña que puedas
inventar. Es una credencial emitida por LocalStack y se obtiene desde la
[aplicación web de LocalStack](https://app.localstack.cloud/), en la sección de
Auth Tokens. Para desarrollo local crea un Developer Auth Token; los entornos
de CI deben utilizar un CI Auth Token. Mantén el token fuera del repositorio y
no lo compartas públicamente.

Añádelo a `backend/.env`:

```env
LOCALSTACK_AUTH_TOKEN=tu_token_de_localstack
```

`docker-compose.yml` transmite esta variable al contenedor de LocalStack y
detiene el arranque con un mensaje claro si no está definida. No es necesario
modificar el código Python/FastAPI: el token solo sirve para autenticar y
activar el servicio de LocalStack.

Para comprobar la activación después de iniciar Docker:

```bash
curl http://localhost:4566/_localstack/info
```

Consulta la [documentación oficial de Auth Tokens de LocalStack](https://docs.localstack.cloud/getting-started/auth-token/)
para crear, rotar o revocar tokens.

## Ejecución local recomendada

Para ejecutar SEC Insights en un equipo local no necesitas instalar un cliente
del sistema para montar S3 ni montar manualmente un bucket S3. La aplicación usa:

- PostgreSQL/PGVector en Docker.
- LocalStack en Docker para simular S3.
- La biblioteca Python `s3fs`, ya incluida en las dependencias del backend,
  para comunicarse con LocalStack, independientemente del sistema operativo.

Después de configurar `.env`, ejecuta desde `backend/`:

```bash
poetry install
make migrate
make seed_db_local
make run
```

`make seed_db_local` crea el bucket local de LocalStack, descarga los informes
SEC de ejemplo de Amazon y Meta, carga los PDF y registra los documentos en la
base de datos. No requiere instalar `s3fs` como herramienta del sistema.

En otra terminal, ejecuta el frontend desde `frontend/`:

```bash
npm i
npm run dev
```

La aplicación estará disponible en `http://localhost:3000` y el backend en
`http://localhost:8000`.

## Flujo opcional: montar un bucket S3 real

La instalación de un cliente `s3fs` compatible con tu sistema operativo solo es
necesaria para el flujo opcional del descargador que monta un bucket S3 real
como una carpeta local. Este flujo no forma parte de la ejecución local normal
de SEC Insights y se describe en la sección
[Descargador de documentos SEC](#descargador-de-documentos-sec-opcional).

## Observabilidad del LLM

Este proyecto inicia automáticamente una versión local de [Arize Phoenix](https://phoenix.arize.com/) y le envía trazas mientras usas la interfaz de chat.
Arize Phoenix es una herramienta open source de observabilidad y evaluación de LLM. El sistema de instrumentación de eventos de LlamaIndex está integrado con Arize Phoenix para facilitar la depuración de tu aplicación LLM durante el desarrollo. Abre el panel de Arize Phoenix en [`http://localhost:6006/`](http://localhost:6006/) al ejecutar SEC Insights localmente para ver las llamadas trazadas a LLM, modelos de embeddings, bases de datos vectoriales y más.

## Scripts
La carpeta `scripts/` contiene varios scripts útiles tanto para operaciones como para desarrollo.

## Chat 🦙
El script `scripts/chat_llama.py` inicia una interfaz REPL para conversar desde el terminal interactuando directamente con la API. Es útil para depurar problemas sin tener que usar el frontend completo.

El script acepta un argumento opcional `--base_url`, cuyo valor predeterminado es `http://localhost:8000`, pero puede apuntar a los servidores de producción o preview. El `Makefile` contiene el comando `chat` para usar esta URL.

Uso:

```
$ poetry shell  # if you aren't already in your poetry shell
$ make chat
poetry run python -m scripts.chat_llama
(Chat🦙) create
Created conversation with ID 8371bbc8-a7fd-4b1f-889b-d0bc882df2a5
(Chat🦙) detail
{
    "id": "8371bbc8-a7fd-4b1f-889b-d0bc882df2a5",
    "created_at": "2023-06-29T20:50:21.330170",
    "updated_at": "2023-06-29T20:50:21.330170",
    "messages": []
}
(Chat🦙) message Hi


=== Message 0 ===
{'id': '05db08be-bbd5-4908-bd68-664d041806f6', 'created_at': None, 'updated_at': None, 'conversation_id': '8371bbc8-a7fd-4b1f-889b-d0bc882df2a5', 'content': 'Hello! How can I assist you today?', 'role': 'assistant', 'status': 'PENDING', 'sub_processes': [{'id': None, 'created_at': None, 'updated_at': None, 'message_id': '05db08be-bbd5-4908-bd68-664d041806f6', 'content': 'Starting to process user message', 'source': 'constructed_query_engine'}]}


=== Message 1 ===
{'id': '05db08be-bbd5-4908-bd68-664d041806f6', 'created_at': '2023-06-29T20:50:36.659499', 'updated_at': '2023-06-29T20:50:36.659499', 'conversation_id': '8371bbc8-a7fd-4b1f-889b-d0bc882df2a5', 'content': 'Hello! How can I assist you today?', 'role': 'assistant', 'status': 'SUCCESS', 'sub_processes': [{'id': '75ace83c-1ebd-4756-898f-1957a69eeb7e', 'created_at': '2023-06-29T20:50:36.659499', 'updated_at': '2023-06-29T20:50:36.659499', 'message_id': '05db08be-bbd5-4908-bd68-664d041806f6', 'content': 'Starting to process user message', 'source': 'constructed_query_engine'}]}


====== Final Message ======
Hello! How can I assist you today?
```

## Descargador de documentos SEC 📃 (opcional)
Tenemos un script para descargar fácilmente archivos SEC 10-K y 10-Q. Es un paso individual del script de carga de datos descrito en la siguiente sección. Salvo que necesites ejecutar solo este paso, probablemente querrás usar el script de carga descrito más abajo 🙂. Sin embargo, las instrucciones de configuración de este script son un requisito previo para ejecutar el script de carga.

Esta sección describe el flujo avanzado para descargar documentos y subirlos a
un bucket S3 real mediante una carpeta montada con un cliente `s3fs`. No es
necesario para la ejecución local estándar; para esa finalidad usa
`make seed_db_local`.

No se necesitan claves de API: utiliza la API Edgar gratuita de la SEC.

Las instrucciones siguientes explican cómo usar el script para descargar informes SEC, convertirlos a PDF y almacenarlos en un bucket de S3.

### Instrucciones de configuración y uso
Pasos de configuración necesarios para usar el descargador y cargar los PDF de la SEC directamente en un bucket de S3.

Estos pasos asumen que ya has seguido las instrucciones anteriores para configurar el entorno de desarrollo.

1. Configura AWS CLI siguiendo las instrucciones oficiales para tu sistema operativo.
    1. Puedes omitir la instalación si ya tienes AWS CLI disponible o si usas la imagen devcontainer de GitHub Codespaces.
    1. Configura AWS CLI.
        - Esto sirve principalmente para establecer las credenciales de AWS que usará s3fs.
        - Ejecuta `aws configure` e introduce la clave de acceso y la clave secreta de un usuario IAM de AWS que tenga acceso a los PDF donde quieras almacenar los archivos SEC.
            - Establece la región predeterminada de AWS en `us-east-1`.
1. Configura un cliente [`s3fs`](https://github.com/s3fs-fuse/s3fs-fuse) compatible con tu sistema operativo.
    1. Consulta la documentación del proyecto o el gestor de paquetes de tu sistema para instalarlo.
        - Puedes omitir este paso si usas la imagen devcontainer de GitHub Codespaces.
    1. Configura una carpeta montada con `s3fs`.
        - Crea localmente la carpeta montada con `mkdir ~/mounted_folder`.
        - `s3fs llama-app-web-assets-preview ~/mounted_folder`
            - Puedes sustituir `llama-app-web-assets-preview` por el nombre del bucket S3 al que quieras cargar los archivos.
1. Instala [`wkhtmltopdf`](https://wkhtmltopdf.org/) siguiendo las instrucciones para tu sistema operativo.
    - Puedes omitir este paso si usas la imagen devcontainer de GitHub Codespaces.
    - En macOS, especialmente en equipos Intel (x86), puede ser necesario descargar e instalar manualmente el paquete `.pkg` desde la [página oficial de descargas](https://wkhtmltopdf.org/downloads). Homebrew puede ofrecer una instalación mediante `brew install --cask wkhtmltopdf`, pero su disponibilidad depende de la arquitectura y de la versión de macOS; compruébala con `brew search --cask wkhtmltopdf`.
    - Después de instalarlo, verifica que el ejecutable esté disponible con `which wkhtmltopdf` y `wkhtmltopdf --version`.
1. Entra en el entorno de Poetry con `poetry shell` desde la raíz del proyecto.
1. Ejecuta el script: `python scripts/download_sec_pdf.py -o ~/mounted_folder --file-types="['10-Q','10-K']"`.
    - Tómate un descanso 🚽 mientras se ejecuta; tardará un rato.
1. Abre la consola de AWS y verifica que los archivos SEC aparecen en el bucket S3.

## Script de carga de la base de datos 🌱
El proyecto incluye varios scripts para cargar un conjunto de documentos en la base de datos. `scripts/seed_db.py` intenta consolidar esos scripts independientes en un único comando.

Este script:
1. Download a set of SEC 10-K & 10-Q documents to a local temp directory
1. Carga esos documentos SEC en la carpeta S3 especificada por `$S3_ASSET_BUCKET_NAME`.
1. Recorre todos los archivos PDF de la carpeta S3 y crea o actualiza una fila en la tabla `Document` según la ruta del archivo dentro del bucket.

### Casos de uso
Esto resulta útil cuando:
1. Quieres configurar un entorno local con tu base de datos PostgreSQL local y tener documentos en la tabla `documents`.
    * En local, usa [`localstack`](https://localstack.cloud/) para almacenar los documentos en un bucket S3 local en lugar de uno real.
1. Quieres actualizar los documentos de las bases de datos de producción o preview.
    * De hecho, este es el script que ejecuta el servicio de tareas programadas [`llama-app-cron`](https://github.com/run-llama/sec-insights/blob/294d8e5/render.yaml#L38), configurado por el blueprint `render.yaml` al desplegar el servicio en Render.com.

### Uso
Para ejecutar el script, asegúrate de haber:
1. Activado el entorno virtual de Python con `poetry shell`.
1. Instalado todas las dependencias necesarias para el script `Descargador de documentos SEC`.
1. Definido en el entorno del shell todas las variables de `.env.development` según el entorno en el que quieras ejecutar el script (por ejemplo, local, preview o producción).

Después puedes ejecutar `python scripts/seed_db.py` para iniciar el proceso de carga.

Para facilitarlo, el Makefile incluye algunos comandos abreviados.
1. `make seed_db`
    - Ejecuta `seed_db.py` sin argumentos CLI, basándose en las variables de entorno configuradas.
1. `make seed_db_preview`
    - Igual que `make seed_db`, pero solo carga documentos SEC de Amazon y Meta.
    - No es necesario cargar tantos documentos de empresas en los entornos preview.
1. `make seed_db_local`
    - Se utiliza para cargar datos en la base de datos local.
    - Ejecuta `seed_db.py` solo para los documentos de `$AMZN` y `$META`.
    - Configura el bucket de LocalStack para servir también los documentos localmente y poder cargarlos en el navegador.
1. `make seed_db_based_on_env`
    - Llama automáticamente a uno de los comandos anteriores según las variables de entorno `RENDER` e `IS_PREVIEW_ENV`.
