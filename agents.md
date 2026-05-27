# AGENTS.md - INTRANET ESCOLAR

## Descripcion General

Este proyecto corresponde a una aplicacion web llamada **Intranet Escolar**, orientada a la administracion de profesores, asignaturas y asignaciones academicas dentro de un establecimiento educacional.

El sistema debe ser simple, modular, mantenible y preparado para futuras ampliaciones.

---

# Objetivo del Proyecto

Desarrollar una intranet escolar utilizando:

- Python
- FastAPI
- PostgreSQL
- HTML
- CSS
- JavaScript

El sistema permitira:

- Gestionar profesores.
- Gestionar asignaturas.
- Asignar asignaturas a profesores.
- Visualizar informacion academica.

---

# Arquitectura del Proyecto

El proyecto debe utilizar arquitectura modular con separacion explicita entre backend y frontend.

## Estructura recomendada

```text
intranet-escolar/
|
|-- backend/
|   |-- app/
|   |   |-- models/
|   |   |-- controllers/
|   |   |-- routes/
|   |   |-- database/
|   |   |-- schemas/
|   |   `-- services/
|   |
|   |-- requirements.txt
|   |-- config.py
|   `-- main.py
|
|-- frontend/
|   |-- templates/
|   |-- static/
|   |   |-- css/
|   |   |-- js/
|   |   `-- img/
|   `-- index.html
|
`-- README.md
```
