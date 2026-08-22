# Frontend de SEC Insights

SEC Insights es una herramienta para analizar múltiples documentos financieros, impulsada por LlamaIndex. [URL pública](https://secinsights.ai/)

## Detalles técnicos

Está construido con `next.js`, `tailwindcss` y React con TypeScript, basado en el [kit inicial de T3](https://create.t3.gg/en/usage/next-js).

## Arquitectura

La aplicación tiene dos rutas principales:

1. `/`, ubicada en `src/pages/index.tsx`. Es la página de inicio e incluye el selector de documentos y una sección de marketing.
2. `/conversation/{conversation_id}`, ubicada en `src/pages/conversation/[id].tsx`. Esta página muestra la ventana de chat a la izquierda y el visor de PDF a la derecha.

- Los PDF se renderizan con `react-pdf`; un PDF individual se renderiza con el componente `VirtualizedPdf.tsx`.
- El componente de chat está en `RenderConversations.tsx`.

## Desarrollo local

1. `npm i`
2. `npm run dev`

3. Antes de enviar cambios al repositorio, ejecuta `npm run build` para detectar errores de TypeScript (pendiente: hook de pre-commit).

Consulta las guías de despliegue para [Vercel](https://create.t3.gg/en/deployment/vercel), [Netlify](https://create.t3.gg/en/deployment/netlify) y [Docker](https://create.t3.gg/en/deployment/docker) para obtener más información.

## Variables de entorno

El frontend carga sus variables desde `frontend/.env`. Crea el archivo a partir
de `.env.example`:

```bash
cp .env.example .env
```

### Variable necesaria

| Variable | Descripción | Valor para desarrollo local |
| --- | --- | --- |
| `NEXT_PUBLIC_BACKEND_URL` | URL base del backend que utilizará el navegador. | `http://localhost:8000/` |

La variable debe comenzar por `NEXT_PUBLIC_` para que Next.js pueda exponerla
al código del navegador. El backend utiliza el prefijo `/api` internamente;
por eso la URL base debe ser `http://localhost:8000/`, sin añadir `/api`.

### Variables opcionales

Estas variables solo son necesarias cuando se ejecuta el frontend dentro de
GitHub Codespaces:

| Variable | Descripción | Valor habitual |
| --- | --- | --- |
| `CODESPACES` | Indica que la aplicación se ejecuta en Codespaces. | `true` |
| `CODESPACE_NAME` | Nombre del Codespace actual. | El valor proporcionado por GitHub. |

Cuando `CODESPACES=true`, `src/config.js` puede advertir si
`NEXT_PUBLIC_BACKEND_URL` no apunta a la URL pública del puerto 8000 del
Codespace, con este formato:

```env
NEXT_PUBLIC_BACKEND_URL=https://NOMBRE_DEL_CODESPACE-8000.app.github.dev/
```

No guardes claves ni secretos en `frontend/.env`, porque las variables
`NEXT_PUBLIC_*` se envían al navegador. La configuración de Sentry del
frontend está actualmente desactivada por defecto en `src/constants.tsx`; no
requiere ninguna variable para desarrollo local.
