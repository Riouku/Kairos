# ARCHIVO MAESTRO - INTRANET ESCOLAR

## 1. Descripcion General del Proyecto

### Nombre del Proyecto
Intranet Escolar

### Objetivo Principal
Desarrollar una intranet escolar orientada a la administracion de profesores, asignaturas y asignaciones academicas dentro de un establecimiento educacional.

El sistema permitira centralizar la informacion academica mediante una plataforma web simple, moderna y accesible.

---

# 2. Objetivos del Sistema

## Objetivos Generales
- Mejorar la organizacion de la informacion academica.
- Digitalizar procesos administrativos del establecimiento.
- Facilitar la gestion de profesores y asignaturas.
- Centralizar informacion academica en una sola plataforma.
- Aplicar conocimientos de desarrollo web y bases de datos.

## Objetivos Especificos
- Registrar profesores.
- Administrar asignaturas.
- Asignar asignaturas a profesores.
- Visualizar listados de informacion.
- Crear una interfaz sencilla e intuitiva.

---

# 3. Alcance del Proyecto

El sistema contara inicialmente con:

- Gestion de profesores.
- Gestion de asignaturas.
- Asignacion de asignaturas a profesores.
- Visualizacion de listados.
- Base de datos centralizada.
- Panel administrativo simple.

No incluira inicialmente:

- Gestion de alumnos.
- Sistema de notas.
- Pagos.
- Autenticacion avanzada.
- Reportes complejos.
- Integracion con servicios externos.

---

# 4. Usuarios del Sistema

## Administrador
Podra:
- Registrar profesores.
- Editar profesores.
- Eliminar profesores.
- Crear asignaturas.
- Asignar asignaturas.
- Visualizar informacion.

---

# 5. Modulos del Sistema

## 5.1 Modulo de Profesores

### Funcionalidades
- Registrar profesores.
- Editar informacion.
- Eliminar profesores.
- Listar profesores.
- Buscar profesores.

### Datos del Profesor
- ID
- Nombre
- Apellido
- Correo electronico
- Telefono (opcional)

---

## 5.2 Modulo de Asignaturas

### Funcionalidades
- Registrar asignaturas.
- Editar asignaturas.
- Eliminar asignaturas.
- Visualizar asignaturas.

### Datos de la Asignatura
- ID
- Nombre de asignatura
- Codigo
- Descripcion

---

## 5.3 Modulo de Asignacion

### Funcionalidades
- Asignar asignaturas a profesores.
- Visualizar asignaciones.
- Eliminar asignaciones.

### Datos de Asignacion
- Profesor
- Asignatura
- Fecha de asignacion

---

# 6. Requerimientos Funcionales

## RF-01
El sistema debe permitir registrar profesores.

## RF-02
El sistema debe permitir editar profesores.

## RF-03
El sistema debe permitir eliminar profesores.

## RF-04
El sistema debe permitir registrar asignaturas.

## RF-05
El sistema debe permitir editar asignaturas.

## RF-06
El sistema debe permitir eliminar asignaturas.

## RF-07
El sistema debe permitir asignar asignaturas a profesores.

## RF-08
El sistema debe mostrar listados de profesores.

## RF-09
El sistema debe mostrar listados de asignaturas.

## RF-10
El sistema debe mostrar listados de asignaciones.

---

# 7. Requerimientos No Funcionales

## RNF-01
La interfaz debe ser simple e intuitiva.

## RNF-02
El sistema debe funcionar desde navegadores web modernos.

## RNF-03
La informacion debe almacenarse en PostgreSQL.

## RNF-04
El sistema debe tener tiempos de respuesta rapidos.

## RNF-05
La plataforma debe permitir despliegue gratuito.

---

# 8. Tecnologias del Proyecto

## Backend
- Python
- FastAPI (recomendado)

## Frontend
- HTML5
- CSS3
- JavaScript

## Base de Datos
- PostgreSQL

## Herramientas
- Visual Studio Code
- pgAdmin
- Git
- GitHub

---

# 9. Arquitectura Recomendada

## Arquitectura General

```text
Frontend (HTML/CSS/JS)
        |
        v
Backend FastAPI
        |
        v
PostgreSQL
```

## Patron Recomendado
Arquitectura modular con separacion explicita entre backend y frontend, manteniendo responsabilidades tipo MVC en el backend.

---

# 10. Estructura Recomendada del Proyecto

```text
intranet-escolar/
|
|-- backend/
|   |-- app/
|   |   |-- models/
|   |   |-- routes/
|   |   |-- controllers/
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
|   |   |-- index.html
|   |   |-- profesores.html
|   |   |-- asignaturas.html
|   |   `-- asignaciones.html
|   |
|   |-- static/
|   |   |-- css/
|   |   |-- js/
|   |   `-- img/
|
`-- README.md
```

---

# 11. Diseno de Base de Datos

## Tabla: profesores

| Campo | Tipo |
|---|---|
| id | SERIAL |
| nombre | VARCHAR(100) |
| apellido | VARCHAR(100) |
| correo | VARCHAR(150) |
| telefono | VARCHAR(20) |

---

## Tabla: asignaturas

| Campo | Tipo |
|---|---|
| id | SERIAL |
| nombre | VARCHAR(100) |
| codigo | VARCHAR(20) |
| descripcion | TEXT |

---

## Tabla: asignaciones

| Campo | Tipo |
|---|---|
| id | SERIAL |
| profesor_id | INTEGER |
| asignatura_id | INTEGER |
| fecha_asignacion | DATE |

---

# 12. Relaciones de Base de Datos

```text
profesores
    |
    | 1:N
    v
asignaciones
    ^
    | N:1
    |
asignaturas
```

---

# 13. Flujo General del Sistema

## Flujo Principal

1. El administrador ingresa al sistema.
2. Registra profesores.
3. Registra asignaturas.
4. Asigna asignaturas a profesores.
5. Visualiza informacion almacenada.

---

# 14. Diseno del Dashboard

## Secciones Principales

- Inicio
- Profesores
- Asignaturas
- Asignaciones

## Caracteristicas del Dashboard

- Menu lateral.
- Tablas dinamicas.
- Formularios simples.
- Diseno responsive.
- Navegacion intuitiva.

---

# 15. Despliegue del Proyecto

## Plataformas Recomendadas

### Render
Caracteristicas:
- Backend gratuito.
- PostgreSQL gratuito.
- Deploy automatico.
- Compatible con Docker.
- Compatible con FastAPI.
- Compatible con Django.
- Compatible con Node.js.

# 16. Recomendaciones Tecnicas

## Backend
Se recomienda utilizar FastAPI debido a:
- Facilidad de aprendizaje.
- Buena integracion con PostgreSQL.
- Ideal para proyectos academicos.
- Estructura modular.
- Validacion de datos con esquemas.
- Documentacion automatica de API.

## Base de Datos
PostgreSQL es recomendado por:
- Estabilidad.
- Seguridad.
- Compatibilidad con Python.
- Gratuito y open source.

---

# 17. Posibles Mejoras Futuras

- Sistema de inicio de sesion.
- Gestion de alumnos.
- Registro de asistencia.
- Gestion de notas.
- Reportes PDF.
- Exportacion Excel.
- Panel estadistico.
- Roles de usuario.
- API REST.
- Notificaciones.

---

# 18. Prompt Maestro para Codex

## Objetivo
Crear una aplicacion web llamada "Intranet Escolar" utilizando Python FastAPI y PostgreSQL.

## Requerimientos Principales

La aplicacion debe:

- Tener un dashboard administrativo.
- Permitir CRUD de profesores.
- Permitir CRUD de asignaturas.
- Permitir asignar asignaturas a profesores.
- Mostrar tablas dinamicas.
- Utilizar PostgreSQL.
- Tener interfaz moderna y responsive.
- Utilizar arquitectura modular con backend y frontend separados.

## Tecnologias Obligatorias

- Python
- FastAPI
- PostgreSQL
- HTML
- CSS
- JavaScript

## Modulos

### Profesores
- Crear profesor.
- Editar profesor.
- Eliminar profesor.
- Listar profesores.

### Asignaturas
- Crear asignatura.
- Editar asignatura.
- Eliminar asignatura.
- Listar asignaturas.

### Asignaciones
- Asignar profesor a asignatura.
- Mostrar asignaciones.
- Eliminar asignaciones.

## Diseno

- Dashboard moderno.
- Menu lateral.
- Formularios responsivos.
- Tablas organizadas.
- Diseno limpio.

## Base de Datos

Crear las tablas:
- profesores
- asignaturas
- asignaciones

Utilizar claves foraneas correctamente.

## Extras Deseados

- Validaciones.
- Mensajes de exito/error.
- Busqueda de datos.
- Diseno responsive.
- Codigo ordenado y documentado.

---

# 19. Conclusion

La Intranet Escolar busca modernizar la administracion academica de un establecimiento educacional mediante una plataforma web simple, eficiente y centralizada.

El proyecto permitira aplicar conocimientos de programacion, bases de datos y desarrollo web, ademas de servir como base para futuras mejoras y ampliaciones del sistema.
