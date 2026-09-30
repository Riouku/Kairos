# Conexion Con Vercel

Este proyecto queda preparado para desplegarse en Vercel como frontend estatico + FastAPI en una funcion Python.

## Variables necesarias

Configura estas variables en Vercel, dentro de Project Settings > Environment Variables:

```text
SUPABASE_DATABASE_URL=postgresql://usuario:password@host:puerto/base?sslmode=require
FRONTEND_ORIGINS=https://tu-proyecto.vercel.app
APP_NAME=Intranet Escolar
```

Cuando `SUPABASE_DATABASE_URL` está definida, la aplicación la prefiere a `DATABASE_URL`. Esto permite usar Supabase aunque una integración como Neon cree y administre `DATABASE_URL`. Si no se define, se usa `DATABASE_URL` y luego `POSTGRES_URL`. Vercel no levanta el servicio `db` de `docker-compose.yml`.

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
5. Pegala en Vercel como `SUPABASE_DATABASE_URL`, con tipo Secret y alcance Preview para la rama que quieras probar; agrega Production si también la desplegarás en producción.

Para migraciones con Alembic, puedes usar la conexion directa de Supabase desde tu equipo si tu red soporta IPv6, o el pooler si no tienes acceso directo. El build de Preview y Production ejecuta `alembic upgrade head` antes de publicar, usando `SUPABASE_DATABASE_URL` cuando está definida. El build de Preview se detiene si falta esa variable o no apunta a Supabase, para evitar migrar por accidente la base de Neon.

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
$env:SUPABASE_DATABASE_URL="postgresql://postgres.PROJECT_REF:DB_PASSWORD@aws-REGION.pooler.supabase.com:6543/postgres?sslmode=require"
alembic upgrade head
```
