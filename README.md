# SEC Insights ES 🏦

**SEC Insights ES** es una adaptación al español latinoamericano y una puesta a punto técnica de [SEC Insights](https://github.com/run-llama/sec-insights), el proyecto open source original de [run-llama](https://github.com/run-llama). Mantiene su propósito —explorar informes SEC 10-K y 10-Q mediante RAG— y documenta aquí las contribuciones específicas de este fork.

## Sobre este fork

Este repositorio parte de [run-llama/sec-insights](https://github.com/run-llama/sec-insights). La adaptación combina una interfaz localizada con correcciones de estabilidad y operación que hacen más reproducible el desarrollo local y más clara la experiencia para usuarios hispanohablantes.

### Contribuciones propias verificadas

- **Interfaz y documentación en español latinoamericano:** traducción de la experiencia de frontend, mensajes del chat, errores, llamadas a la acción y documentación principal, de frontend y de backend ([commit de traducción](https://github.com/ricardocamposc/sec-insights-es/commit/85762df7675dcb8fbe12fc548ab146fd1fc735a7), [docs y guía para agentes](https://github.com/ricardocamposc/sec-insights-es/commit/2b9f1d172bff5bd733bb646ba08b4d4ee846d311)).
- **S3 y asyncio:** reutilización controlada de recursos S3, cierre explícito de clientes y del event loop compartido de `s3fs/fsspec`, y prevención de problemas derivados de reutilizar clientes entre solicitudes ([S3 y recursos asíncronos](https://github.com/ricardocamposc/sec-insights-es/commit/6d88f741075e578a223b29be2af6f19fd43cd877), [cierre de recursos](https://github.com/ricardocamposc/sec-insights-es/commit/aed2e1331b1b62487d4deea0db7ee61e9bc7d05b)).
- **Observabilidad con Arize Phoenix y OpenInference:** integración, activación configurable mediante `ENABLE_PHOENIX` y serialización segura de eventos de callbacks ([integración Phoenix](https://github.com/ricardocamposc/sec-insights-es/commit/244ec3cb3f8881846be3295a11a70e61773a497d), [estabilización de serialización](https://github.com/ricardocamposc/sec-insights-es/commit/c79465be7134b00fb24aef64863581b53c323e75)).
- **Limpieza de SSE y base de datos:** cierre de sesiones de base de datos usadas por el streaming SSE, liberación de recursos durante el apagado y persistencia esperada de eventos de callbacks ([SSE](https://github.com/ricardocamposc/sec-insights-es/commit/37208302793f5ff230f24d3d0286b6d3f69521dc), [DB y callbacks](https://github.com/ricardocamposc/sec-insights-es/commit/25dc993b6629a6d7b26446cbaa0ce00f261a30c4), [persistencia](https://github.com/ricardocamposc/sec-insights-es/commit/c7526812a56552422ced17fcb29acaa70b2fc928)).
- **Desarrollo local actualizado:** compatibilidad con la autenticación actual de LocalStack mediante `LOCALSTACK_AUTH_TOKEN` ([commit](https://github.com/ricardocamposc/sec-insights-es/commit/99b4359c5e3542adf36c1fb00996e28f50e31cfc)).
- **Intercom opcional:** el widget se inicializa únicamente cuando `NEXT_PUBLIC_ENABLE_INTERCOM` está habilitado ([commit](https://github.com/ricardocamposc/sec-insights-es/commit/0b58a98c5e3542adf36c1fb00996e28f50e31cfc)).

La atribución, licencia y documentación técnica del proyecto original se conservan; esta sección identifica únicamente el trabajo añadido en este fork.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/ricardocamposc/sec-insights-es)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

SEC Insights utiliza las capacidades de generación aumentada mediante recuperación (RAG) de [LlamaIndex](https://github.com/jerryjliu/llama_index) para responder preguntas sobre documentos SEC 10-K y 10-Q.

Puedes empezar a usar la aplicación en [secinsights.ai](https://www.secinsights.ai/)

También puedes consultar nuestra [guía de tutorial de extremo a extremo en YouTube](https://youtu.be/2O52Tfj79T4?si=CYUcaBkc9P9g_m0P). El vídeo cubre las funcionalidades del producto, la arquitectura del sistema, la configuración del entorno de desarrollo y el uso de documentos propios *(incluso distintos de los informes SEC)*. Incluye capítulos para ir directamente a la sección que más te interese.

## ¿Por qué creamos este proyecto? 🤔
A medida que las aplicaciones RAG pasan de prototipos a producción, pensamos que nuestra comunidad de desarrolladores encontraría útil disponer de un ejemplo completo de una aplicación RAG real y funcional.

SEC Insights funciona tanto localmente como en la nube. También incluye muchas funcionalidades aplicables de inmediato a la mayoría de las aplicaciones RAG.

Puedes usar este repositorio como referencia para crear tu propia aplicación RAG full-stack o hacer un fork y utilizarlo como base sólida para tu proyecto.

## Funcionalidades del producto 😎
- Preguntas y respuestas sobre documentos mediante chat
- Citas de las fuentes en las que se basa cada respuesta del modelo
- Visor de PDF con resaltado de citas
- Uso de herramientas basadas en API ([polygon.io](https://polygon.io/)) para responder preguntas cuantitativas
- Streaming de las respuestas del LLM a nivel de token mediante [Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- Streaming de los pasos de razonamiento (subpreguntas) dentro del chat

## Funcionalidades para desarrollo 🤓
- Infraestructura como código para desplegar directamente en [Vercel](https://vercel.com/) y [Render](https://render.com/)
- Despliegues continuos proporcionados por Vercel y Render.com; publicar cambios es tan sencillo como fusionarlos en la rama `main`
- Entornos de producción y preview para frontend y backend, para probar cambios antes de publicarlos
- Configuración local robusta con [LocalStack](https://localstack.cloud/) y [Docker](https://www.docker.com/) Compose
- Monitorización y perfilado mediante [Sentry](https://sentry.io/welcome/)
- Pruebas de carga mediante [Loader.io](https://loader.io/)
- Observabilidad de LLM con [Arize Phoenix](https://phoenix.arize.com/)
- Variedad de scripts de Python para chat interactivo y gestión de datos

## Stack tecnológico ⚒️
- Frontend
    - [React](https://react.dev/) / [Next.js](https://nextjs.org/)
    - [Tailwind CSS](https://tailwindcss.com/)
- Backend
    - [FastAPI](https://fastapi.tiangolo.com/)
    - [Docker](https://www.docker.com/)
    - [SQLAlchemy](https://www.sqlalchemy.org/)
    - [OpenAI](https://openai.com/) (gpt-3.5-turbo + text-embedding-ada-002)
    - [PGVector](https://github.com/pgvector/pgvector)
    - [LlamaIndex 🦙](https://www.llamaindex.ai/)
- Infraestructura
    - [Render.com](https://render.com/)
        - Alojamiento del backend
        - [Postgres 15](https://www.postgresql.org/)
    - [Vercel](https://vercel.com/)
        - Alojamiento del frontend
    - [AWS](https://aws.amazon.com/)
        - [Cloudfront](https://aws.amazon.com/cloudfront/)
        - [S3](https://aws.amazon.com/s3/)

### Arquitectura del sistema
[![System Architecture](https://www.plantuml.com/plantuml/png/jLJ1RjD04BtxAuPmo2bLsgGIaH0YYMqe0XhL4HoggjhOKsVRzMoqEsuR4F_EncxTDEjGX8GFbdRUcpTldZVfGeXNaX2KMEkI8PC6KvQQRF0ggv7FKJo_d9zUdfry-3WFWgR3wiAzUAtS6vabvJQmDv9MmeW2LYAz4Jd2pm3SCt6dtEYIigbMsi3hy70wZ4O0NKYGOT70a5OuQoW4fqlW9O8mHj_LG2scJORcGMXGFLKzriI9_85mE6pEFYjXDAXvlS8jFAuU3s_qsf1gyubMsGuuLZ8dI95S9VWLR6MIAbrc_psHez6R_cJKdi1pFvbWiH1sxqUAmsWIzlq9uU1usE__pOJQQ2t_R4-lUJWS7KTLTRwKwGsXjN3qN8nqji_gt0YoZeN4EtPzx0NB1bCMbAkzgKJZA8p2bjodW-Zu3way2NVEa5pVGQgB3WWBzV5XtdaiB8zd9zLW1rpKrQdH19_qeZusNswcBUS6xMP0VRqwu-y998FEezoiN2YPmYoCOL8wHNuGd1bvAnWXOMr4ZbDDZFVSS9xqedj6Gq91WkPMfcWRwIIQTYr4MIuCECSNyBQNwJlgxRXrixHQvveEf8POag1KEhbGiDXfQryzGMAptZH_qIHP6qdvfadX5UzjEbqXZKyUFRyumwTxcxX47l_KEj_GfAYQ8Bwwv0wkBSIEp4wq8dSXSNpd5KHsNLekaDX2QJULfSmofFhdOGE_7thdDUMYpR5NsQOtDwAnlWstteTsvaitfDLskUgzynstKXsnpOpNN36RhThXFLxz3Vsv7kMV51j_mNjdgYnKy1i0)](https://www.plantuml.com/plantuml/uml/jLJ1RjD04BtxAuPmo2bLsgGIaH0YYMqe0XhL4HoggjhOKsVRzMoqEsuR4F_EncxTDEjGX8GFbdRUcpTldZVfGeXNaX2KMEkI8PC6KvQQRF0ggv7FKJo_d9zUdfry-3WFWgR3wiAzUAtS6vabvJQmDv9MmeW2LYAz4Jd2pm3SCt6dtEYIigbMsi3hy70wZ4O0NKYGOT70a5OuQoW4fqlW9O8mHj_LG2scJORcGMXGFLKzriI9_85mE6pEFYjXDAXvlS8jFAuU3s_qsf1gyubMsGuuLZ8dI95S9VWLR6MIAbrc_psHez6R_cJKdi1pFvbWiH1sxqUAmsWIzlq9uU1usE__pOJQQ2t_R4-lUJWS7KTLTRwKwGsXjN3qN8nqji_gt0YoZeN4EtPzx0NB1bCMbAkzgKJZA8p2bjodW-Zu3way2NVEa5pVGQgB3WWBzV5XtdaiB8zd9zLW1rpKrQdH19_qeZusNswcBUS6xMP0VRqwu-y998FEezoiN2YPmYoCOL8wHNuGd1bvAnWXOMr4ZbDDZFVSS9xqedj6Gq91WkPMfcWRwIIQTYr4MIuCECSNyBQNwJlgxRXrixHQvveEf8POag1KEhbGiDXfQryzGMAptZH_qIHP6qdvfadX5UzjEbqXZKyUFRyumwTxcxX47l_KEj_GfAYQ8Bwwv0wkBSIEp4wq8dSXSNpd5KHsNLekaDX2QJULfSmofFhdOGE_7thdDUMYpR5NsQOtDwAnlWstteTsvaitfDLskUgzynstKXsnpOpNN36RhThXFLxz3Vsv7kMV51j_mNjdgYnKy1i0)

## Uso 💻
Consulta los archivos `README.md` de las carpetas `frontend/` y `backend/` para conocer las instrucciones específicas de configuración. También puedes consultar el [tutorial de YouTube](https://youtu.be/2O52Tfj79T4?si=1Tm3zvuqna5ei4Cu&t=677), que explica cómo configurar el entorno de desarrollo.

El repositorio incluye una configuración para [GitHub Codespaces](https://github.com/features/codespaces) en [`.devcontainer/devcontainer.json`](https://github.com/ricardocamposc/sec-insights-es/blob/main/.devcontainer/devcontainer.json). Al usar GitHub Codespaces, el entorno ya incluye muchas de las bibliotecas y dependencias del sistema necesarias. Es una de las formas más rápidas de poner en marcha el proyecto. También se ha configurado correctamente en Linux, macOS y Windows.

Si tienes problemas, revisa primero las respuestas del [FAQ](./FAQ.md) o busca en los [issues de este fork](https://github.com/ricardocamposc/sec-insights-es/issues). Si no encuentras una solución, puedes [abrir un issue](https://github.com/ricardocamposc/sec-insights-es/issues/new). Para consultar el historial y las decisiones del proyecto base, visita [run-llama/sec-insights](https://github.com/run-llama/sec-insights).

También existe un [canal #sec-insights en Discord](https://discord.com/channels/1059199217496772688/1150942525968879636) para consultas breves.

## Consideraciones 🧐
- El frontend actualmente no es compatible con dispositivos móviles.
- El objetivo principal es ofrecer una base sólida para aplicaciones RAG full-stack; el rendimiento RAG todavía puede mejorarse.

## Contribuciones 💡
Estamos abiertos a contribuciones y esperamos con interés las ideas que la comunidad de LlamaIndex pueda aportar.

Un agradecimiento especial a [**@Evanc123**](https://github.com/Evanc123) por su excelente trabajo desarrollando el frontend.
