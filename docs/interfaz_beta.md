# Documentación de Interfaz — Intranet Escolar

## Descripción General

La interfaz corresponde a una intranet escolar moderna y minimalista enfocada en:

- Profesores
- Asignaturas
- Asignaciones

El diseño utiliza una estructura tipo dashboard administrativo.

---

# 1. Estructura General del Layout

La aplicación está dividida en 2 secciones principales:

## Sidebar lateral izquierdo

Barra vertical fija con:

- Logo del sistema
- Nombre “INTRANET ESCOLAR”
- Menú de navegación

### Opciones del menú

- Inicio
- Profesores
- Asignaturas
- Asignaciones

### Características visuales

- Fondo azul oscuro degradado
- Texto blanco
- Íconos blancos
- Botón activo azul brillante
- Bordes redondeados
- Sidebar fija de ancho aproximado:
  - 240px desktop

---

## Contenido principal

Zona derecha donde cambia el contenido según el módulo.

Características:

- Fondo gris muy claro
- Padding interno amplio
- Cards blancas
- Bordes redondeados
- Sombra suave
- Diseño responsive

---

# 2. Navbar Superior

En la parte superior del contenido principal existe una barra horizontal.

## Componentes

### Botón menú hamburguesa

- Icono ☰
- Visible en responsive

### Nombre de la sección actual

Ejemplos:

- Inicio
- Profesores
- Asignaturas
- Asignaciones

### Usuario administrador

Lado derecho:

- Avatar circular
- Texto: “admin”
- Flecha desplegable

---

# 3. Pantalla Dashboard (Inicio)

## Header

Texto:

- “Bienvenido, admin”
- Subtexto: “Panel de Control”

---

## Tarjetas resumen (stats cards)

Se muestran 3 tarjetas horizontales:

### Card Profesores

Contenido:

- Ícono usuarios
- Número total profesores
- Texto descriptivo

Color:
- Azul

---

### Card Asignaturas

Contenido:

- Ícono libro
- Número total asignaturas

Color:
- Verde

---

### Card Asignaciones

Contenido:

- Ícono enlace/asignación
- Total asignaciones

Color:
- Naranja

---

## Gráfico de resumen

Card blanca con:

- Título:
  - “Resumen del Sistema”
- Gráfico de líneas simple
- Estadísticas mensuales

---

## Tabla de asignaciones recientes

Card blanca con:

Columnas:

- Asignatura
- Profesor
- Fecha

---

# 4. Módulo Profesores

Pantalla CRUD.

## Componentes

### Header

- Título:
  - “Lista de Profesores”
- Botón:
  - “Nuevo Profesor”

---

## Barra de búsqueda

Input con:

- Placeholder:
  - “Buscar profesor…”

Ícono lupa al lado derecho.

---

## Tabla de profesores

### Columnas

- ID
- Nombre
- Apellido
- Correo Electrónico
- Acciones

---

## Botones de acciones

### Editar

- Botón azul
- Icono lápiz

### Eliminar

- Botón rojo
- Icono basurero

---

## Paginación

Parte inferior:

- Anterior
- Número de páginas
- Siguiente

---

# 5. Módulo Asignaturas

Similar al CRUD de profesores.

## Header

- “Lista de Asignaturas”
- Botón:
  - “Nueva Asignatura”

---

## Tabla

### Columnas

- ID
- Asignatura
- Descripción
- Acciones

---

## Funcionalidades

- Crear asignatura
- Editar asignatura
- Eliminar asignatura
- Buscar asignatura

---

# 6. Módulo Asignaciones

Pantalla dividida en 2 columnas.

---

## Columna izquierda → Formulario

### Componentes

#### Select Profesor

Dropdown:

- “Seleccione un profesor”

---

#### Select Asignatura

Dropdown:

- “Seleccione una asignatura”

---

#### Fecha

Input tipo date.

---

#### Botón guardar

Texto:
- “Guardar Asignación”

Color:
- Verde

---

## Columna derecha → Tabla asignaciones

### Columnas

- ID
- Profesor
- Asignatura
- Fecha

---

## Botón inferior

- “Ver todas las asignaciones”

Color:
- Azul

---

# 7. Estilo Visual General

## Diseño

- Minimalista
- Moderno
- Administrativo
- Tipo dashboard SaaS

---

## Colores principales

### Azul oscuro sidebar

```css
#0B1F3A
```

### Azul botones

```css
#2563EB
```

### Verde

```css
#16A34A
```

### Naranja

```css
#F59E0B
```

### Fondo

```css
#F5F7FB
```

---

# 8. Tipografía

Estilo recomendado:

- Inter
- Poppins
- Nunito

---

# 9. Componentes técnicos recomendados para Codex

## Frontend

- React
- Next.js
- TailwindCSS

---

## Componentes UI

- Cards
- Sidebar
- Navbar
- DataTable
- Modal CRUD
- Forms
- Selects
- Charts

---

# 10. Responsive Design

## Desktop

- Sidebar fija
- Tablas completas

## Tablet

- Sidebar colapsable

## Mobile

- Menú hamburguesa
- Cards verticales
- Tablas con scroll horizontal

---

# 11. Estructura recomendada de carpetas

```txt
src/
 ├── components/
 │    ├── sidebar/
 │    ├── navbar/
 │    ├── cards/
 │    ├── tables/
 │    └── forms/
 │
 ├── pages/
 │    ├── dashboard/
 │    ├── profesores/
 │    ├── asignaturas/
 │    └── asignaciones/
 │
 ├── services/
 │
 ├── hooks/
 │
 ├── layouts/
 │
 └── styles/
```

---

# 12. Funcionalidades CRUD necesarias

## Profesores

- Crear profesor
- Editar profesor
- Eliminar profesor
- Listar profesores
- Buscar profesores

---

## Asignaturas

- Crear asignatura
- Editar asignatura
- Eliminar asignatura
- Buscar asignaturas

---

## Asignaciones

- Asignar profesor a asignatura
- Ver asignaciones
- Eliminar asignaciones
- Filtrar asignaciones
