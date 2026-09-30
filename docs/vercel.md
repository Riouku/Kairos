# Conexion Con Vercel

Este proyecto queda preparado para desplegarse en Vercel como frontend estatico + FastAPI en una funcion Python.

## Variables necesarias

Configura estas variables en Vercel, dentro de Project Settings > Environment Variables:

```text
DATABASE_URL=postgresql://usuario:password@host:puerto/base?sslmode=require
FRONTEND_ORIGINS=https://tu-proyecto.vercel.app
APP_NAME=Intranet Escolar
```

La base de datos debe ser PostgreSQL externa, por ejemplo Supabase, Neon, Railway o Vercel Postgres. Vercel no levanta el servicio `db` de `docker-compose.yml`.

## Supabase

Para Supabase, usa la cadena de conexion PostgreSQL del pooler en modo transaction, recomendada para funciones serverless como Vercel:

```text
DATABASE_URL=postgresql://postgres.PROJECT_REF:DB_PASSWORD@aws-REGION.pooler.supabase.com:6543/postgres?sslmode=require
```

Donde:

- `PROJECT_REF` es el identificador del proyecto Supabase.
- `DB_PASSWORD` es la password de la base de datos; si contiene caracteres especiales, copiala desde el panel de Supabase ya codificada.
- `aws-REGION.pooler.supabase.com` debe ser el host exacto que entrega Supabase.
- `6543` corresponde al pooler transaction.

En Supabase Dashboard:

1. Entra al proyecto.
2. Abre Connect.
3. Copia la URI de Transaction pooler.
4. Agrega `?sslmode=require` si la URL no lo incluye.
5. Pegala en Vercel como `DATABASE_URL`, para Production, Preview y Development si corresponde.

Para migraciones con Alembic, puedes usar la conexion directa de Supabase desde tu equipo si tu red soporta IPv6, o el pooler si no tienes acceso directo. Lo importante es que la variable `DATABASE_URL` apunte a la misma base antes de ejecutar `alembic upgrade head`.

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
$env:DATABASE_URL="postgresql://postgres.PROJECT_REF:DB_PASSWORD@aws-REGION.pooler.supabase.com:6543/postgres?sslmode=require"
alembic upgrade head
```
