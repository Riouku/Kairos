# Despliegue En Vercel

## Preparacion Del Proyecto

El proyecto queda preparado para Vercel con:

- `api/index.py`: entrypoint serverless para FastAPI.
- `requirements.txt`: instala dependencias del backend.
- `.python-version`: fija Python 3.12 para evitar errores con dependencias nativas.
- `build_vercel.py`: copia `frontend/templates/*.html` y `frontend/static/` a `public/`.
- `vercel.json`: configura build, salida estatica y rutas hacia FastAPI.

## Variables De Entorno En Vercel

Configura estas variables en Vercel Project Settings:

```text
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DATABASE
FRONTEND_ORIGINS=https://TU-PROYECTO.vercel.app
APP_NAME=Intranet Escolar
```

Si usas un dominio propio, agregalo tambien a `FRONTEND_ORIGINS`.

## Base De Datos

Vercel no levanta el contenedor PostgreSQL de `docker-compose.yml`. Debes usar una base PostgreSQL externa, por ejemplo Neon, Supabase, Railway o Vercel Marketplace.

Despues de configurar `DATABASE_URL`, aplica migraciones desde tu maquina:

```powershell
cd backend
..\.venv\Scripts\python.exe -m alembic upgrade head
```

## Despliegue

Opcion recomendada:

1. Sube el repositorio a GitHub.
2. En Vercel, crea un nuevo proyecto desde ese repositorio.
3. Deja el root directory en la raiz del repo.
4. Agrega las variables de entorno.
5. Deploy.

URLs esperadas:

- Frontend: `https://TU-PROYECTO.vercel.app/`
- API docs: `https://TU-PROYECTO.vercel.app/docs`
- Health: `https://TU-PROYECTO.vercel.app/health`
