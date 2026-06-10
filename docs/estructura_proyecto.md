# Estructura Del Proyecto

Este archivo resume como esta organizado Kairos actualmente.

```text
Kairos/
|-- api/
|   `-- index.py                  # Adaptador FastAPI para Vercel
|
|-- backend/
|   |-- app/
|   |   |-- controllers/           # Logica de negocio por modulo
|   |   |-- database/              # Sesion SQLAlchemy
|   |   |-- models/                # Modelos ORM
|   |   |-- routes/                # Endpoints FastAPI
|   |   |-- schemas/               # Schemas Pydantic
|   |   `-- services/              # Servicios compartidos futuros
|   |-- alembic/                   # Migraciones
|   |-- config.py                  # Configuracion por entorno
|   |-- main.py                    # App FastAPI
|   `-- requirements.txt
|
|-- frontend/
|   |-- static/
|   |   |-- css/
|   |   |-- img/
|   |   `-- js/
|   |-- templates/                 # Paginas HTML
|   `-- index.html                 # Redireccion local
|
|-- docs/                          # Documentacion del proyecto
|-- scripts/                       # Scripts de apoyo
|-- docker-compose.yml             # Entorno local completo
|-- vercel.json                    # Configuracion Vercel
|-- pyproject.toml                 # Entrypoint Vercel
`-- README.md
```

## Modulos Actuales

- Dashboard
- Profesores
- Asignaturas
- Asignaciones
- Cursos
- Calendario academico
- Estudiantes, periodos, evaluaciones y notas
- Asistencia diaria por curso

## Archivos Generados O Locales

No se deben versionar:

- `.venv/`
- `backend/.venv/`
- `__pycache__/`
- `*.log`
- `.env`
- `outputs/`
- `public/`

`public/` se genera con:

```powershell
python scripts\build_vercel.py
```
