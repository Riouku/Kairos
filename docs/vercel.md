# Conexion Con Vercel

Este proyecto queda preparado para desplegarse en Vercel como frontend estatico + FastAPI en una funcion Python.

## Variables necesarias

Configura estas variables en Vercel, dentro de Project Settings > Environment Variables:

```text
DATABASE_URL=postgresql://usuario:password@host:5432/base
FRONTEND_ORIGINS=https://tu-proyecto.vercel.app
APP_NAME=Intranet Escolar
```

La base de datos debe ser PostgreSQL externa, por ejemplo Neon, Supabase, Railway o Vercel Postgres. Vercel no levanta el servicio `db` de `docker-compose.yml`.

## Rutas esperadas

```text
/
/notas.html
/templates/notas.html
/api/profesores
/health
/docs
```

## Como importar en Vercel

1. Sube el proyecto a GitHub.
2. En Vercel, elige Add New > Project.
3. Importa el repositorio.
4. Deja Root Directory en la raiz del repositorio.
5. Agrega las variables de entorno.
6. Deploy.

El entrypoint de FastAPI queda declarado en `pyproject.toml`:

```toml
[tool.vercel]
entrypoint = "backend.main:app"
```

## Migraciones

Antes de usar la app en produccion, ejecuta las migraciones contra la base de datos remota:

```powershell
cd backend
$env:DATABASE_URL="postgresql://usuario:password@host:5432/base"
alembic upgrade head
```
