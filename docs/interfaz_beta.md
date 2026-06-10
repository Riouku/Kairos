# Documentacion de Interfaz - Intranet Escolar

## Descripcion General

La interfaz corresponde a una intranet escolar administrativa, simple y modular.
Esta construida con HTML, CSS y JavaScript sin framework frontend.

Modulos visibles:

- Inicio
- Profesores
- Asignaturas
- Asignaciones
- Calendario
- Notas

## Layout

La aplicacion usa una estructura tipo dashboard:

- Sidebar lateral con logo y menu principal.
- Contenido principal con encabezado de seccion.
- Cards de resumen en inicio.
- Tablas para listados.
- Formularios para crear y editar registros.

## Navegacion

Todas las pantallas principales viven en `frontend/templates/`:

- `index.html`
- `profesores.html`
- `asignaturas.html`
- `asignaciones.html`
- `calendario.html`
- `notas.html`
- `login.html`

El archivo `frontend/index.html` redirige al dashboard para que `http://localhost:8001/` abra la aplicacion en modo local.

## Pantalla Inicio

La pantalla de inicio muestra:

- Estado de conexion con la API.
- Total de profesores.
- Total de asignaturas.
- Total de asignaciones.
- Eventos del mes.
- Proximos eventos o clases.
- Asignaciones recientes.
- Promedio general y ultimas notas.

## Profesores

Funcionalidades:

- Listar profesores.
- Buscar profesores.
- Crear profesor.
- Editar profesor.
- Activar o desactivar profesor.
- Eliminar profesor.

Campos principales:

- Nombre
- Apellido
- Correo
- Telefono
- Especialidad
- Estado

## Asignaturas

Funcionalidades:

- Listar asignaturas.
- Buscar asignaturas.
- Crear asignatura.
- Editar asignatura.
- Activar o desactivar asignatura.
- Eliminar asignatura.

Campos principales:

- Nombre
- Codigo
- Descripcion
- Nivel
- Horas semanales
- Estado

## Asignaciones

Funcionalidades:

- Asignar una asignatura a un profesor.
- Listar asignaciones.
- Eliminar asignaciones.
- Ver resumen mensual.

Campos principales:

- Profesor
- Asignatura
- Fecha de asignacion

## Calendario Academico

Funcionalidades:

- Ver calendario mensual.
- Ver lista de eventos del mes.
- Crear cursos.
- Crear eventos academicos.
- Crear horarios semanales.
- Filtrar por tipo, curso, profesor, asignatura y anio.

Validaciones esperadas:

- Eventos con titulo, tipo y fecha de inicio.
- Horarios con curso, profesor, asignatura, dia y horas.
- Hora de fin mayor que hora de inicio.
- Bloqueo de choques por profesor.
- Bloqueo de choques por curso.

## Notas

Funcionalidades:

- Crear estudiantes asociados a cursos.
- Crear periodos academicos.
- Crear evaluaciones con ponderacion.
- Registrar o actualizar notas por evaluacion.
- Ver resumen de promedios ponderados.
- Filtrar por anio, curso, asignatura, profesor y periodo.

Validaciones esperadas:

- Notas entre `1.0` y `7.0`.
- Maximo un decimal por nota.
- Una nota por estudiante y evaluacion.
- Estudiante perteneciente al curso de la evaluacion.
- Ponderacion activa acumulada hasta `100`.

## Estilo Visual

La interfaz mantiene un estilo administrativo:

- Colores sobrios.
- Tablas claras.
- Formularios directos.
- Cards para informacion resumida.
- Sidebar persistente.
- Diseno responsive.

## URLs Locales

- Frontend: `http://localhost:8001/`
- Dashboard: `http://localhost:8001/templates/index.html`
- Notas: `http://localhost:8001/templates/notas.html`
- API docs: `http://localhost:8000/docs`
- API health: `http://localhost:8000/health`

## Criterios de Orden

- Mantener HTML en `frontend/templates/`.
- Mantener CSS en `frontend/static/css/`.
- Mantener JavaScript en `frontend/static/js/`.
- Mantener imagenes e iconos en `frontend/static/img/`.
- No guardar logs ni cache en Git.
- No duplicar logica de API en las paginas HTML.
