# Intranet Escolar

Aplicacion web para gestionar profesores, asignaturas y asignaciones academicas. El backend usa FastAPI y PostgreSQL; el frontend usa HTML, CSS y JavaScript con `fetch`.

## Estructura

```text
backend/
  app/
    controllers/
    database/
    models/
    routes/
    schemas/
  alembic/
  main.py
  requirements.txt

frontend/
  templates/
  static/
```

## Backend

Activar el entorno virtual:

```powershell
cd C:\Users\manue\OneDrive\Documentos\Kairos\backend
.\.venv\Scripts\Activate.ps1
```

Instalar dependencias si hace falta:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Crear un archivo `.env` a partir de `.env.example` y ajustar `DATABASE_URL`:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/intranet_escolar
```

Aplicar migraciones:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
```

Ejecutar API:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Endpoints principales:

- `GET /health`
- `GET /api/dashboard/resumen`
- `GET|POST /api/profesores`
- `GET|PUT|DELETE /api/profesores/{id}`
- `GET|POST /api/asignaturas`
- `GET|PUT|DELETE /api/asignaturas/{id}`
- `GET|POST /api/asignaciones`
- `DELETE /api/asignaciones/{id}`

Documentacion automatica:

- `http://localhost:8000/docs`

## Frontend

Desde la raiz del proyecto puedes servir el frontend con:

```powershell
cd C:\Users\manue\OneDrive\Documentos\Kairos\frontend
python -m http.server 8001
```

Luego abrir:

- `http://localhost:8001/templates/index.html`

El frontend consume por defecto la API en:

```text
http://localhost:8000/api
```

## Flujo de demo

1. Verificar que el estado de API aparezca como conectado.
2. Registrar profesores.
3. Registrar asignaturas.
4. Crear asignaciones entre profesores y asignaturas.
5. Volver al inicio para ver el resumen actualizado.
