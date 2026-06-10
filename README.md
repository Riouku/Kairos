# Intranet Escolar

Aplicacion web para administrar informacion academica de un establecimiento educacional.

El proyecto esta separado en dos capas principales:

- `backend/`: API con FastAPI, SQLAlchemy, Alembic y PostgreSQL.
- `frontend/`: interfaz HTML, CSS y JavaScript servida como archivos estaticos.

## Estructura

```text
Kairos/
|-- api/
|   `-- index.py
|
|-- backend/
|   |-- app/
|   |   |-- controllers/
|   |   |-- database/
|   |   |-- models/
|   |   |-- routes/
|   |   |-- schemas/
|   |   `-- services/
|   |-- alembic/
|   |-- config.py
|   |-- main.py
|   `-- requirements.txt
|
|-- frontend/
|   |-- static/
|   |   |-- css/
|   |   |-- img/
|   |   `-- js/
|   |-- templates/
|   `-- index.html
|
|-- docs/
|-- scripts/
|-- AGENTS.md
|-- docker-compose.yml
|-- pyproject.toml
|-- vercel.json
`-- README.md
```

## Modulos

- Dashboard principal.
- Gestion completa de profesores.
- Gestion completa de asignaturas.
- Gestion de asignaciones entre profesores y asignaturas.
- Gestion basica de cursos.
- Calendario academico con eventos y horarios semanales.
- Gestion de estudiantes, evaluaciones y notas ponderadas.
- Registro diario de asistencia por curso.

## Backend

Crear o revisar `backend/.env`:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/intranet_escolar
FRONTEND_ORIGINS=http://localhost:8001,http://127.0.0.1:8001
```

Instalar dependencias:

```powershell
cd C:\Users\manue\OneDrive\Documentos\Kairos\backend
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Aplicar migraciones:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
```

Ejecutar API local:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

URLs principales del backend:

- `http://localhost:8000/health`
- `http://localhost:8000/health/db`
- `http://localhost:8000/docs`

## API

Endpoints principales:

- `GET /api/dashboard/resumen`
- `GET|POST /api/profesores`
- `GET|PUT|DELETE /api/profesores/{id}`
- `PATCH /api/profesores/{id}/estado`
- `GET|POST /api/asignaturas`
- `GET|PUT|DELETE /api/asignaturas/{id}`
- `PATCH /api/asignaturas/{id}/estado`
- `GET|POST /api/asignaciones`
- `DELETE /api/asignaciones/{id}`
- `GET|POST /api/cursos`
- `GET|PUT|DELETE /api/cursos/{id}`
- `GET|POST /api/estudiantes`
- `GET|PUT|DELETE /api/estudiantes/{id}`
- `PATCH /api/estudiantes/{id}/estado`
- `GET|POST /api/periodos`
- `GET|PUT|DELETE /api/periodos/{id}`
- `GET|POST /api/evaluaciones`
- `GET|PUT|DELETE /api/evaluaciones/{id}`
- `PATCH /api/evaluaciones/{id}/estado`
- `GET|POST /api/notas`
- `PUT|DELETE /api/notas/{id}`
- `GET /api/notas/resumen`
- `GET|POST /api/asistencias`
- `POST /api/asistencias/bulk`
- `PUT|DELETE /api/asistencias/{id}`
- `GET /api/asistencias/resumen`
- `GET /api/calendario`
- `GET /api/calendario/proximos`
- `GET|POST /api/calendario/eventos`
- `PUT|DELETE /api/calendario/eventos/{id}`
- `GET|POST /api/calendario/horarios`
- `PUT|DELETE /api/calendario/horarios/{id}`

## Frontend

Servir la interfaz local:

```powershell
cd C:\Users\manue\OneDrive\Documentos\Kairos\frontend
python -m http.server 8001
```

Abrir:

- `http://localhost:8001/`
- `http://localhost:8001/templates/index.html`
- `http://localhost:8001/templates/profesores.html`
- `http://localhost:8001/templates/asignaturas.html`
- `http://localhost:8001/templates/asignaciones.html`
- `http://localhost:8001/templates/calendario.html`
- `http://localhost:8001/templates/notas.html`
- `http://localhost:8001/templates/asistencia.html`

El frontend consume automaticamente:

```text
Local:  http://localhost:8000/api
Vercel: /api
```

## Docker

Levantar PostgreSQL, API y frontend:

```powershell
docker compose up --build
```

Abrir:

- Frontend: `http://localhost:8001/`
- API docs: `http://localhost:8000/docs`
- Health API: `http://localhost:8000/health`
- Health DB: `http://localhost:8000/health/db`

La API en Docker usa:

```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/intranet_escolar
```

## Vercel

El proyecto incluye configuracion para desplegar en Vercel:

- `vercel.json`: define el build del frontend estatico y las rutas hacia FastAPI.
- `pyproject.toml`: define el entrypoint `backend.main:app`.
- `api/index.py`: adaptador compatible con Vercel.
- `scripts/build_vercel.py`: genera la carpeta `public/` durante el build.

Variables necesarias en Vercel:

```text
DATABASE_URL=postgresql://usuario:password@host:5432/base
FRONTEND_ORIGINS=https://tu-proyecto.vercel.app
APP_NAME=Intranet Escolar
```

Vercel no levanta el PostgreSQL de `docker-compose.yml`, por lo que se debe usar una base PostgreSQL externa.

Mas detalle: `docs/vercel.md`.

## Archivos locales ignorados

No se versionan entornos, cache, logs, salidas generadas ni variables locales:

- `.venv/`
- `backend/.venv/`
- `__pycache__/`
- `*.log`
- `.env`
- `outputs/`
- `public/`

## Flujo de prueba manual

1. Levantar los servicios.
2. Verificar `http://localhost:8000/health`.
3. Abrir `http://localhost:8001/`.
4. Crear un profesor.
5. Crear una asignatura.
6. Crear una asignacion.
7. Crear un curso.
8. Crear un evento o horario en calendario.
9. Crear estudiante, periodo, evaluacion y nota.
10. Registrar asistencia diaria para un curso.
11. Revisar el dashboard.
