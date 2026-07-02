const isLocalHost = ["localhost", "127.0.0.1"].includes(window.location.hostname);
const API_BASE_URL = window.KAIROS_API_BASE_URL || (isLocalHost ? "http://localhost:8000/api" : "/api");
const HEALTH_URL = window.KAIROS_HEALTH_URL || (isLocalHost ? "http://localhost:8000/health/db" : "/health/db");

const state = {
  cursos: [],
  cursoEstudiantes: [],
  estudiantesAdmin: {
    cursos: [],
    estudiantes: [],
  },
  profesores: [],
  asignaturas: [],
  asignaciones: [],
  notas: {
    anio: 2026,
    estudiantes: [],
    ingresoEstudiantes: [],
    periodos: [],
    evaluaciones: [],
    registros: [],
    resumen: [],
  },
  calendario: {
    anio: 2026,
    mes: 6,
    cursos: [],
    items: [],
  },
  asistencia: {
    anio: 2026,
    cursos: [],
    estudiantes: [],
    registros: [],
  },
};

function qs(selector) {
  return document.querySelector(selector);
}

function qsa(selector) {
  return [...document.querySelectorAll(selector)];
}

function setText(selector, value) {
  const element = qs(selector);
  if (element) element.textContent = value;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function showMessage(selector, text, isError = false) {
  const element = qs(selector);
  if (!element) return;
  element.textContent = text;
  element.classList.toggle("error", isError);
  element.classList.remove("hidden");
}

function clearMessage(selector) {
  const element = qs(selector);
  if (element) element.classList.add("hidden");
}

function openModal(selector) {
  const modal = qs(selector);
  if (!modal) return;
  modal.classList.remove("hidden");
  modal.setAttribute("aria-hidden", "false");
}

function closeModal(modal) {
  modal.classList.add("hidden");
  modal.setAttribute("aria-hidden", "true");
}

async function api(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });

  if (response.status === 204) return null;

  const rawText = await response.text();
  let data = {};
  if (rawText) {
    try {
      data = JSON.parse(rawText);
    } catch {
      data = {};
    }
  }
  if (!response.ok) {
    const detail = data.detail;
    const message = Array.isArray(detail)
      ? detail.map((item) => item.msg || item.detail || JSON.stringify(item)).join(" ")
      : detail || data.error || rawText || "No se pudo completar la solicitud.";
    throw new Error(`Error ${response.status}: ${message}`);
  }
  return data;
}

async function checkApiStatus() {
  const status = qs("#api-status");
  if (!status) return;
  try {
    const response = await fetch(HEALTH_URL);
    if (!response.ok) throw new Error("API no disponible");
    status.textContent = "API conectada";
    status.classList.add("ok");
    status.classList.remove("error");
  } catch {
    status.textContent = "API no disponible";
    status.classList.add("error");
    status.classList.remove("ok");
  }
}

function bindShell() {
  qs(".menu-toggle")?.addEventListener("click", () => {
    qs("#sidebar")?.classList.toggle("open");
  });

  qs("[data-logout]")?.addEventListener("click", () => {
    sessionStorage.removeItem("kairos-user");
    window.location.href = "login.html";
  });

  qsa("[data-close-modal]").forEach((button) => {
    button.addEventListener("click", () => closeModal(button.closest(".modal")));
  });

  qsa(".modal").forEach((modal) => {
    modal.addEventListener("click", (event) => {
      if (event.target === modal) closeModal(modal);
    });
  });
}

function debounce(callback, delay = 250) {
  let timeoutId;
  return (...args) => {
    window.clearTimeout(timeoutId);
    timeoutId = window.setTimeout(() => callback(...args), delay);
  };
}

function formatDate(value) {
  if (!value) return "-";
  return new Date(`${value}T00:00:00`).toLocaleDateString("es-CL");
}

function renderMonthlyChart(items = []) {
  const chart = qs("#monthly-chart");
  if (!chart) return;
  const max = Math.max(...items.map((item) => item.total), 1);
  chart.innerHTML = items
    .map((item) => {
      const height = Math.max((item.total / max) * 104, item.total > 0 ? 18 : 8);
      return `
        <div class="month-bar">
          <div class="month-bar-fill" style="height: ${height}px" title="${item.total} asignaciones"></div>
          <strong>${item.total}</strong>
          <span>${escapeHtml(item.mes)}</span>
        </div>
      `;
    })
    .join("");
}

function bindLogin() {
  qs("#login-form")?.addEventListener("submit", (event) => {
    event.preventDefault();
    sessionStorage.setItem("kairos-user", qs("#login-email").value.trim() || "admin@kairos.cl");
    showMessage("#login-message", "Acceso correcto. Redirigiendo al panel...");
    window.setTimeout(() => {
      window.location.href = "index.html";
    }, 450);
  });
}

async function initDashboard() {
  try {
    const resumen = await api("/dashboard/resumen");
    setText("#total-profesores", resumen.total_profesores);
    setText("#total-asignaturas", resumen.total_asignaturas);
    setText("#total-estudiantes", resumen.total_estudiantes || 0);
    setText("#total-asignaciones", resumen.total_asignaciones);
    setText("#total-mes", resumen.asignaciones_mes_destacado);
    setText("#mes-activo", resumen.mes_mas_activo);
    setText("#promedio-general", resumen.promedio_general ? resumen.promedio_general.toFixed(1) : "-");
    setText("#porcentaje-asistencia", resumen.porcentaje_asistencia === null || resumen.porcentaje_asistencia === undefined ? "-" : `${resumen.porcentaje_asistencia}%`);
    renderMonthlyChart(resumen.estadisticas_mensuales || []);

    const table = qs("#dashboard-asignaciones");
    const empty = qs("#dashboard-empty");
    table.innerHTML = resumen.ultimas_asignaciones
      .map(
        (item) => `
          <tr>
            <td>${item.asignatura_nombre}</td>
            <td>${item.profesor_nombre}</td>
            <td>${formatDate(item.fecha_asignacion)}</td>
          </tr>
        `
      )
      .join("");
    empty.classList.toggle("hidden", resumen.ultimas_asignaciones.length > 0);

    const notasTable = qs("#dashboard-notas");
    const notasEmpty = qs("#dashboard-notas-empty");
    if (notasTable) {
      notasTable.innerHTML = (resumen.ultimas_notas || [])
        .map(
          (item) => `
            <tr>
              <td>${escapeHtml(item.estudiante_nombre || "-")}</td>
              <td>${escapeHtml(item.evaluacion_titulo || "-")}</td>
              <td><strong>${Number(item.nota).toFixed(1)}</strong></td>
            </tr>
          `
        )
        .join("");
      notasEmpty?.classList.toggle("hidden", (resumen.ultimas_notas || []).length > 0);
    }
  } catch {
    setText("#total-profesores", "0");
    setText("#total-asignaturas", "0");
    setText("#total-estudiantes", "0");
    setText("#total-asignaciones", "0");
    setText("#total-mes", "0");
    setText("#mes-activo", "Sin datos");
    setText("#promedio-general", "-");
    setText("#porcentaje-asistencia", "-");
    renderMonthlyChart(["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"].map((mes) => ({ mes, total: 0 })));
    setText("#dashboard-empty", "No se pudo cargar el resumen. Verifica que el backend este ejecutandose.");
    qs("#dashboard-empty")?.classList.remove("hidden");
  }
}

function getProfesorFilters() {
  const search = qs("#profesor-search")?.value.trim() || "";
  const activo = qs("#profesor-estado-filter")?.value || "";
  const params = new URLSearchParams();
  if (search) params.set("search", search);
  if (activo) params.set("activo", activo);
  return params.toString() ? `?${params.toString()}` : "";
}

function getCursoFilters() {
  const search = qs("#curso-search")?.value.trim() || "";
  const activo = qs("#curso-estado-filter")?.value || "";
  const anio = qs("#curso-anio-filter")?.value || "2026";
  const params = new URLSearchParams();
  if (search) params.set("search", search);
  if (activo) params.set("activo", activo);
  if (anio) params.set("anio_academico", anio);
  return params.toString() ? `?${params.toString()}` : "";
}

function cursoStudentCount(cursoId) {
  return state.cursoEstudiantes.filter((estudiante) => estudiante.curso_id === Number(cursoId)).length;
}

async function loadCursos() {
  const query = getCursoFilters();
  const anio = qs("#curso-anio-filter")?.value || "2026";
  const [cursos, estudiantes] = await Promise.all([
    api(`/cursos${query}`),
    api(`/estudiantes?anio_academico=${anio}`),
  ]);
  state.cursos = cursos;
  state.cursoEstudiantes = estudiantes;

  setText("#cursos-total", cursos.length);
  setText("#cursos-activos", cursos.filter((curso) => curso.activo).length);
  setText("#cursos-estudiantes", estudiantes.length);

  const table = qs("#cursos-table");
  table.innerHTML = cursos
    .map(
      (curso) => `
        <tr>
          <td>${curso.id}</td>
          <td>${escapeHtml(curso.nombre)}</td>
          <td>${escapeHtml(curso.nivel)}</td>
          <td>${escapeHtml(curso.letra || "-")}</td>
          <td>${escapeHtml(curso.jornada)}</td>
          <td>${curso.anio_academico}</td>
          <td>${cursoStudentCount(curso.id)}</td>
          <td><span class="status-badge ${curso.activo ? "status-active" : "status-inactive"}">${curso.activo ? "Activo" : "Inactivo"}</span></td>
          <td class="actions">
            <button class="button button-light action-button" data-view-curso="${curso.id}" title="Ver detalle">Ver</button>
            <button class="button button-blue action-button" data-edit-curso="${curso.id}" title="Editar curso">Editar</button>
            <button class="button ${curso.activo ? "button-light" : "button-green"} action-button" data-toggle-curso="${curso.id}" title="${curso.activo ? "Desactivar" : "Activar"}">${curso.activo ? "Desactivar" : "Activar"}</button>
            <button class="button button-red action-button" data-delete-curso="${curso.id}" title="Eliminar curso">Eliminar</button>
          </td>
        </tr>
      `
    )
    .join("");
  qs("#cursos-empty").classList.toggle("hidden", cursos.length > 0);
}

function resetCursoForm() {
  qs("#curso-id").value = "";
  qs("#curso-form").reset();
  qs("#curso-jornada").value = "Manana";
  qs("#curso-anio").value = qs("#curso-anio-filter")?.value || "2026";
  qs("#curso-activo").value = "true";
  setText("#curso-form-title", "Nuevo Curso");
}

function fillCursoForm(curso) {
  qs("#curso-id").value = curso.id;
  qs("#curso-nombre").value = curso.nombre;
  qs("#curso-nivel").value = curso.nivel;
  qs("#curso-letra").value = curso.letra || "";
  qs("#curso-jornada").value = curso.jornada;
  qs("#curso-anio").value = curso.anio_academico;
  qs("#curso-activo").value = String(curso.activo);
}

function showCursoDetail(curso) {
  qs("#curso-detail").innerHTML = `
    <div><span>Curso</span><strong>${escapeHtml(curso.nombre)}</strong></div>
    <div><span>Nivel</span><strong>${escapeHtml(curso.nivel)}</strong></div>
    <div><span>Letra</span><strong>${escapeHtml(curso.letra || "Sin letra")}</strong></div>
    <div><span>Jornada</span><strong>${escapeHtml(curso.jornada)}</strong></div>
    <div><span>Año academico</span><strong>${curso.anio_academico}</strong></div>
    <div><span>Estudiantes</span><strong>${cursoStudentCount(curso.id)}</strong></div>
    <div><span>Estado</span><strong>${curso.activo ? "Activo" : "Inactivo"}</strong></div>
  `;
  openModal("#curso-detail-modal");
}

function bindCursos() {
  qs("#nuevo-curso").addEventListener("click", () => {
    resetCursoForm();
    openModal("#curso-modal");
  });

  qs("#curso-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    clearMessage("#curso-message");
    const id = qs("#curso-id").value;
    const payload = {
      nombre: qs("#curso-nombre").value.trim(),
      nivel: qs("#curso-nivel").value.trim(),
      letra: qs("#curso-letra").value.trim() || null,
      jornada: qs("#curso-jornada").value,
      anio_academico: Number(qs("#curso-anio").value || 2026),
      activo: qs("#curso-activo").value === "true",
    };
    try {
      await api(id ? `/cursos/${id}` : "/cursos", {
        method: id ? "PUT" : "POST",
        body: JSON.stringify(payload),
      });
      showMessage("#curso-message", id ? "Curso actualizado correctamente." : "Curso registrado correctamente.");
      resetCursoForm();
      closeModal(qs("#curso-modal"));
      await loadCursos();
    } catch (error) {
      showMessage("#curso-message", error.message, true);
      window.alert(error.message);
    }
  });

  qs("#curso-search").addEventListener("input", debounce(() => loadCursos()));
  qs("#curso-estado-filter").addEventListener("change", () => loadCursos());
  qs("#curso-anio-filter").addEventListener("change", () => loadCursos());

  qs("#cursos-table").addEventListener("click", async (event) => {
    const button = event.target.closest("button");
    if (!button) return;
    const viewId = button.dataset.viewCurso;
    const editId = button.dataset.editCurso;
    const toggleId = button.dataset.toggleCurso;
    const deleteId = button.dataset.deleteCurso;
    if (viewId) {
      const curso = state.cursos.find((item) => item.id === Number(viewId));
      if (curso) showCursoDetail(curso);
    }
    if (editId) {
      const curso = state.cursos.find((item) => item.id === Number(editId));
      if (!curso) return;
      fillCursoForm(curso);
      setText("#curso-form-title", "Editar Curso");
      openModal("#curso-modal");
    }
    if (toggleId) {
      const curso = state.cursos.find((item) => item.id === Number(toggleId));
      if (!curso) return;
      const nextState = !curso.activo;
      try {
        await api(`/cursos/${toggleId}`, {
          method: "PUT",
          body: JSON.stringify({ activo: nextState }),
        });
        showMessage("#curso-message", nextState ? "Curso activado correctamente." : "Curso desactivado correctamente.");
        await loadCursos();
      } catch (error) {
        showMessage("#curso-message", error.message, true);
      }
    }
    if (deleteId && window.confirm("Deseas eliminar este curso?")) {
      try {
        await api(`/cursos/${deleteId}`, { method: "DELETE" });
        showMessage("#curso-message", "Curso eliminado correctamente.");
        await loadCursos();
      } catch (error) {
        showMessage("#curso-message", error.message, true);
      }
    }
  });
}

function getEstudianteAdminFilters() {
  const search = qs("#estudiante-admin-search")?.value.trim() || "";
  const cursoId = qs("#estudiante-admin-curso-filter")?.value || "";
  const activo = qs("#estudiante-admin-estado-filter")?.value || "";
  const anio = qs("#estudiante-admin-anio-filter")?.value || "2026";
  const params = new URLSearchParams();
  if (search) params.set("search", search);
  if (cursoId) params.set("curso_id", cursoId);
  if (activo) params.set("activo", activo);
  if (anio) params.set("anio_academico", anio);
  return params.toString() ? `?${params.toString()}` : "";
}

function fillEstudianteAdminCursoSelects(selectedCurso = "") {
  const cursos = state.estudiantesAdmin.cursos;
  fillSelect("#estudiante-admin-curso-filter", cursos, (curso) => curso.nombre, "Todos los cursos", qs("#estudiante-admin-curso-filter")?.value || "");
  fillSelect("#estudiante-admin-curso", cursos, (curso) => curso.nombre, "Seleccione", selectedCurso);
}

async function loadEstudianteAdminCursos(selectedCurso = "") {
  const anio = qs("#estudiante-admin-anio-filter")?.value || "2026";
  const cursos = await api(`/cursos?activo=true&anio_academico=${anio}`);
  state.estudiantesAdmin.cursos = cursos;
  fillEstudianteAdminCursoSelects(selectedCurso);
}

async function loadEstudiantesAdmin() {
  const query = getEstudianteAdminFilters();
  const estudiantes = await api(`/estudiantes${query}`);
  state.estudiantesAdmin.estudiantes = estudiantes;

  const cursosConEstudiantes = new Set(estudiantes.map((estudiante) => estudiante.curso_id).filter(Boolean));
  setText("#estudiantes-total", estudiantes.length);
  setText("#estudiantes-activos", estudiantes.filter((estudiante) => estudiante.activo).length);
  setText("#estudiantes-cursos", cursosConEstudiantes.size);

  const table = qs("#estudiantes-admin-table");
  table.innerHTML = estudiantes
    .map(
      (estudiante) => `
        <tr>
          <td>${estudiante.id}</td>
          <td>${escapeHtml(estudiante.rut || "-")}</td>
          <td>${escapeHtml(estudiante.nombre)} ${escapeHtml(estudiante.apellido)}</td>
          <td>${escapeHtml(estudiante.correo || "-")}</td>
          <td>${escapeHtml(estudiante.curso_nombre || "-")}</td>
          <td>${estudiante.anio_academico}</td>
          <td><span class="status-badge ${estudiante.activo ? "status-active" : "status-inactive"}">${estudiante.activo ? "Activo" : "Inactivo"}</span></td>
          <td class="actions">
            <a class="button button-light action-button" href="perfil-estudiante.html?id=${estudiante.id}" title="Ver perfil">Perfil</a>
            <button class="button button-light action-button" data-view-estudiante-admin="${estudiante.id}" title="Ver detalle">Ver</button>
            <button class="button button-blue action-button" data-edit-estudiante-admin="${estudiante.id}" title="Editar estudiante">Editar</button>
            <button class="button ${estudiante.activo ? "button-light" : "button-green"} action-button" data-toggle-estudiante-admin="${estudiante.id}" title="${estudiante.activo ? "Desactivar" : "Activar"}">${estudiante.activo ? "Desactivar" : "Activar"}</button>
            <button class="button button-red action-button" data-delete-estudiante-admin="${estudiante.id}" title="Eliminar estudiante">Eliminar</button>
          </td>
        </tr>
      `
    )
    .join("");
  qs("#estudiantes-admin-empty").classList.toggle("hidden", estudiantes.length > 0);
}

function resetEstudianteAdminForm() {
  qs("#estudiante-admin-id").value = "";
  qs("#estudiante-admin-form").reset();
  qs("#estudiante-admin-anio").value = qs("#estudiante-admin-anio-filter")?.value || "2026";
  qs("#estudiante-admin-activo").value = "true";
  fillEstudianteAdminCursoSelects(qs("#estudiante-admin-curso-filter")?.value || "");
  setText("#estudiante-admin-form-title", "Nuevo Estudiante");
}

function fillEstudianteAdminForm(estudiante) {
  qs("#estudiante-admin-id").value = estudiante.id;
  qs("#estudiante-admin-rut").value = estudiante.rut || "";
  qs("#estudiante-admin-nombre").value = estudiante.nombre;
  qs("#estudiante-admin-apellido").value = estudiante.apellido;
  qs("#estudiante-admin-correo").value = estudiante.correo || "";
  qs("#estudiante-admin-anio").value = estudiante.anio_academico;
  qs("#estudiante-admin-activo").value = String(estudiante.activo);
  fillEstudianteAdminCursoSelects(estudiante.curso_id);
  setText("#estudiante-admin-form-title", "Editar Estudiante");
}

function showEstudianteAdminDetail(estudiante) {
  qs("#estudiante-admin-detail").innerHTML = `
    <div><span>Nombre completo</span><strong>${escapeHtml(estudiante.nombre)} ${escapeHtml(estudiante.apellido)}</strong></div>
    <div><span>RUT</span><strong>${escapeHtml(estudiante.rut || "Sin registrar")}</strong></div>
    <div><span>Correo</span><strong>${escapeHtml(estudiante.correo || "Sin registrar")}</strong></div>
    <div><span>Curso</span><strong>${escapeHtml(estudiante.curso_nombre || "Sin curso")}</strong></div>
    <div><span>Año academico</span><strong>${estudiante.anio_academico}</strong></div>
    <div><span>Estado</span><strong>${estudiante.activo ? "Activo" : "Inactivo"}</strong></div>
  `;
  openModal("#estudiante-admin-detail-modal");
}

async function refreshEstudiantesAdmin(loadCursos = false) {
  clearMessage("#estudiante-admin-message");
  if (loadCursos) await loadEstudianteAdminCursos();
  await loadEstudiantesAdmin();
}

function bindEstudiantesAdmin() {
  qs("#nuevo-estudiante-admin").addEventListener("click", () => {
    resetEstudianteAdminForm();
    openModal("#estudiante-admin-modal");
  });

  qs("#estudiante-admin-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    clearMessage("#estudiante-admin-message");
    const id = qs("#estudiante-admin-id").value;
    const payload = {
      rut: qs("#estudiante-admin-rut").value.trim() || null,
      nombre: qs("#estudiante-admin-nombre").value.trim(),
      apellido: qs("#estudiante-admin-apellido").value.trim(),
      correo: qs("#estudiante-admin-correo").value.trim() || null,
      curso_id: Number(qs("#estudiante-admin-curso").value),
      anio_academico: Number(qs("#estudiante-admin-anio").value || 2026),
      activo: qs("#estudiante-admin-activo").value === "true",
    };
    try {
      await api(id ? `/estudiantes/${id}` : "/estudiantes", {
        method: id ? "PUT" : "POST",
        body: JSON.stringify(payload),
      });
      showMessage("#estudiante-admin-message", id ? "Estudiante actualizado correctamente." : "Estudiante registrado correctamente.");
      resetEstudianteAdminForm();
      closeModal(qs("#estudiante-admin-modal"));
      await refreshEstudiantesAdmin(true);
    } catch (error) {
      showMessage("#estudiante-admin-message", error.message, true);
      window.alert(error.message);
    }
  });

  qs("#estudiante-admin-search").addEventListener("input", debounce(() => loadEstudiantesAdmin()));
  qs("#estudiante-admin-curso-filter").addEventListener("change", () => loadEstudiantesAdmin());
  qs("#estudiante-admin-estado-filter").addEventListener("change", () => loadEstudiantesAdmin());
  qs("#estudiante-admin-anio-filter").addEventListener("change", async () => {
    await loadEstudianteAdminCursos();
    await loadEstudiantesAdmin();
  });

  qs("#estudiantes-admin-table").addEventListener("click", async (event) => {
    const button = event.target.closest("button");
    if (!button) return;
    const viewId = button.dataset.viewEstudianteAdmin;
    const editId = button.dataset.editEstudianteAdmin;
    const toggleId = button.dataset.toggleEstudianteAdmin;
    const deleteId = button.dataset.deleteEstudianteAdmin;
    if (viewId) {
      const estudiante = state.estudiantesAdmin.estudiantes.find((item) => item.id === Number(viewId));
      if (estudiante) showEstudianteAdminDetail(estudiante);
    }
    if (editId) {
      const estudiante = state.estudiantesAdmin.estudiantes.find((item) => item.id === Number(editId));
      if (!estudiante) return;
      fillEstudianteAdminForm(estudiante);
      openModal("#estudiante-admin-modal");
    }
    if (toggleId) {
      const estudiante = state.estudiantesAdmin.estudiantes.find((item) => item.id === Number(toggleId));
      if (!estudiante) return;
      const nextState = !estudiante.activo;
      try {
        await api(`/estudiantes/${toggleId}/estado?activo=${nextState}`, { method: "PATCH" });
        showMessage("#estudiante-admin-message", nextState ? "Estudiante activado correctamente." : "Estudiante desactivado correctamente.");
        await loadEstudiantesAdmin();
      } catch (error) {
        showMessage("#estudiante-admin-message", error.message, true);
      }
    }
    if (deleteId && window.confirm("Deseas eliminar este estudiante?")) {
      try {
        await api(`/estudiantes/${deleteId}`, { method: "DELETE" });
        showMessage("#estudiante-admin-message", "Estudiante eliminado correctamente.");
        await refreshEstudiantesAdmin();
      } catch (error) {
        showMessage("#estudiante-admin-message", error.message, true);
      }
    }
  });
}

async function initEstudiantesAdmin() {
  bindEstudiantesAdmin();
  await loadEstudianteAdminCursos();
  await loadEstudiantesAdmin();
  const editId = Number(new URLSearchParams(window.location.search).get("edit") || 0);
  if (editId) {
    const estudiante = state.estudiantesAdmin.estudiantes.find((item) => item.id === editId) || await api(`/estudiantes/${editId}`).catch(() => null);
    if (estudiante) {
      await loadEstudianteAdminCursos(estudiante.curso_id);
      fillEstudianteAdminForm(estudiante);
      openModal("#estudiante-admin-modal");
    }
  }
}

function perfilEstudianteId() {
  return Number(new URLSearchParams(window.location.search).get("id") || 0);
}

function asistenciaPercent(registros) {
  if (!registros.length) return null;
  const asistidos = registros.filter((item) => ["presente", "tarde", "justificado"].includes(item.estado)).length;
  return Math.round((asistidos / registros.length) * 1000) / 10;
}

function renderPerfilNotas(notas) {
  const table = qs("#perfil-notas-table");
  if (!table) return;
  const recientes = notas.slice(0, 8);
  table.innerHTML = recientes
    .map(
      (nota) => `
        <tr>
          <td>${escapeHtml(nota.evaluacion_titulo || "-")}</td>
          <td>${escapeHtml(nota.asignatura_nombre || "-")}</td>
          <td>${escapeHtml(nota.periodo_nombre || "-")}</td>
          <td><strong>${Number(nota.nota).toFixed(1)}</strong></td>
        </tr>
      `
    )
    .join("");
  qs("#perfil-notas-empty")?.classList.toggle("hidden", recientes.length > 0);
}

function renderPerfilResumen(items) {
  const table = qs("#perfil-resumen-table");
  if (!table) return;
  table.innerHTML = items
    .map(
      (item) => `
        <tr>
          <td>${escapeHtml(item.asignatura_nombre || "-")}</td>
          <td>${escapeHtml(item.periodo_nombre || "-")}</td>
          <td><strong>${item.promedio === null || item.promedio === undefined ? "-" : Number(item.promedio).toFixed(1)}</strong></td>
          <td>${item.notas_registradas || 0}</td>
        </tr>
      `
    )
    .join("");
  qs("#perfil-resumen-empty")?.classList.toggle("hidden", items.length > 0);
}

function renderPerfilAsistencia(registros) {
  const table = qs("#perfil-asistencia-table");
  if (!table) return;
  const recientes = registros.slice(0, 10);
  table.innerHTML = recientes
    .map(
      (registro) => `
        <tr>
          <td>${formatDate(registro.fecha)}</td>
          <td><span class="status-badge ${registro.estado === "ausente" ? "status-inactive" : "status-active"}">${escapeHtml(registro.estado)}</span></td>
          <td>${escapeHtml(registro.observacion || "-")}</td>
        </tr>
      `
    )
    .join("");
  qs("#perfil-asistencia-empty")?.classList.toggle("hidden", recientes.length > 0);
}

function renderPerfilCurso(estudiante, curso) {
  const detail = qs("#perfil-curso-detail");
  if (!detail) return;
  detail.innerHTML = `
    <div><span>Curso</span><strong>${escapeHtml(estudiante.curso_nombre || curso?.nombre || "-")}</strong></div>
    <div><span>Nivel</span><strong>${escapeHtml(curso?.nivel || "-")}</strong></div>
    <div><span>Letra</span><strong>${escapeHtml(curso?.letra || "-")}</strong></div>
    <div><span>Jornada</span><strong>${escapeHtml(curso?.jornada || "-")}</strong></div>
    <div><span>Año academico</span><strong>${estudiante.anio_academico}</strong></div>
    <div><span>Estado curso</span><strong>${curso ? (curso.activo ? "Activo" : "Inactivo") : "-"}</strong></div>
  `;
}

async function initPerfilEstudiante() {
  const id = perfilEstudianteId();
  if (!id) {
    showMessage("#perfil-message", "No se indico un estudiante para mostrar. Vuelve a Estudiantes y abre un perfil.", true);
    return;
  }

  try {
    const estudiante = await api(`/estudiantes/${id}`);
    const [notas, resumen, asistencias, curso] = await Promise.all([
      api(`/notas?estudiante_id=${id}&anio_academico=${estudiante.anio_academico}`),
      api(`/notas/resumen?estudiante_id=${id}&anio_academico=${estudiante.anio_academico}`),
      api(`/asistencias?estudiante_id=${id}&anio_academico=${estudiante.anio_academico}`),
      estudiante.curso_id ? api(`/cursos/${estudiante.curso_id}`).catch(() => null) : Promise.resolve(null),
    ]);

    setText("#perfil-nombre", `${estudiante.nombre} ${estudiante.apellido}`);
    setText("#perfil-rut", `RUT ${estudiante.rut || "-"}`);
    setText("#perfil-correo", `Correo ${estudiante.correo || "-"}`);
    setText("#perfil-curso", `Curso ${estudiante.curso_nombre || "-"}`);
    setText("#perfil-anio", `Año ${estudiante.anio_academico}`);
    const estado = qs("#perfil-estado");
    if (estado) {
      estado.textContent = estudiante.activo ? "Activo" : "Inactivo";
      estado.classList.toggle("status-active", estudiante.activo);
      estado.classList.toggle("status-inactive", !estudiante.activo);
    }
    const asistencia = asistenciaPercent(asistencias);
    setText("#perfil-promedio", resumen.promedio_general === null || resumen.promedio_general === undefined ? "-" : Number(resumen.promedio_general).toFixed(1));
    setText("#perfil-total-notas", notas.length);
    setText("#perfil-asistencia", asistencia === null ? "-" : `${asistencia}%`);
    setText("#perfil-total-asistencias", asistencias.length);
    const editLink = qs("#perfil-editar-link");
    if (editLink) editLink.href = `estudiantes.html?edit=${estudiante.id}`;

    renderPerfilNotas(notas);
    renderPerfilResumen(resumen.items || []);
    renderPerfilAsistencia(asistencias);
    renderPerfilCurso(estudiante, curso);
  } catch (error) {
    showMessage("#perfil-message", `No se pudo cargar el perfil: ${error.message}`, true);
  }
}

async function loadProfesores() {
  const query = getProfesorFilters();
  const profesores = await api(`/profesores${query}`);
  const table = qs("#profesores-table");
  table.innerHTML = profesores
    .map(
      (profesor) => `
        <tr>
          <td>${profesor.id}</td>
          <td>${escapeHtml(profesor.rut || "-")}</td>
          <td>${escapeHtml(profesor.nombre)} ${escapeHtml(profesor.apellido)}</td>
          <td>${escapeHtml(profesor.correo)}</td>
          <td>${escapeHtml(profesor.especialidad || "-")}</td>
          <td><span class="status-badge ${profesor.activo ? "status-active" : "status-inactive"}">${profesor.activo ? "Activo" : "Inactivo"}</span></td>
          <td class="actions">
            <button class="button button-light action-button" data-view-profesor="${profesor.id}" title="Ver detalle">Ver</button>
            <button class="button button-blue action-button" data-edit-profesor="${profesor.id}" title="Editar profesor">Editar</button>
            <button class="button ${profesor.activo ? "button-light" : "button-green"} action-button" data-toggle-profesor="${profesor.id}" title="${profesor.activo ? "Desactivar" : "Activar"}">${profesor.activo ? "Desactivar" : "Activar"}</button>
            <button class="button button-red action-button" data-delete-profesor="${profesor.id}" title="Eliminar profesor">Eliminar</button>
          </td>
        </tr>
      `
    )
    .join("");
  qs("#profesores-empty").classList.toggle("hidden", profesores.length > 0);
  state.profesores = profesores;
}

function resetProfesorForm() {
  qs("#profesor-id").value = "";
  qs("#profesor-form").reset();
  qs("#profesor-activo").value = "true";
  setText("#profesor-form-title", "Nuevo Profesor");
}

function fillProfesorForm(profesor) {
  qs("#profesor-id").value = profesor.id;
  qs("#profesor-nombre").value = profesor.nombre;
  qs("#profesor-apellido").value = profesor.apellido;
  qs("#profesor-rut").value = profesor.rut || "";
  qs("#profesor-correo").value = profesor.correo;
  qs("#profesor-telefono").value = profesor.telefono || "";
  qs("#profesor-especialidad").value = profesor.especialidad || "";
  qs("#profesor-activo").value = String(profesor.activo);
}

function showProfesorDetail(profesor) {
  qs("#profesor-detail").innerHTML = `
    <div><span>Nombre completo</span><strong>${escapeHtml(profesor.nombre)} ${escapeHtml(profesor.apellido)}</strong></div>
    <div><span>RUT</span><strong>${escapeHtml(profesor.rut || "Sin registrar")}</strong></div>
    <div><span>Correo</span><strong>${escapeHtml(profesor.correo)}</strong></div>
    <div><span>Telefono</span><strong>${escapeHtml(profesor.telefono || "Sin registrar")}</strong></div>
    <div><span>Especialidad</span><strong>${escapeHtml(profesor.especialidad || "Sin registrar")}</strong></div>
    <div><span>Estado</span><strong>${profesor.activo ? "Activo" : "Inactivo"}</strong></div>
  `;
  openModal("#profesor-detail-modal");
}

function bindProfesores() {
  qs("#nuevo-profesor").addEventListener("click", () => {
    resetProfesorForm();
    openModal("#profesor-modal");
  });

  qs("#profesor-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    clearMessage("#profesor-message");
    const id = qs("#profesor-id").value;
    const payload = {
      nombre: qs("#profesor-nombre").value.trim(),
      apellido: qs("#profesor-apellido").value.trim(),
      rut: qs("#profesor-rut").value.trim() || null,
      correo: qs("#profesor-correo").value.trim(),
      telefono: qs("#profesor-telefono").value.trim() || null,
      especialidad: qs("#profesor-especialidad").value.trim() || null,
      activo: qs("#profesor-activo").value === "true",
    };
    try {
      await api(id ? `/profesores/${id}` : "/profesores", {
        method: id ? "PUT" : "POST",
        body: JSON.stringify(payload),
      });
      showMessage("#profesor-message", id ? "Profesor actualizado correctamente." : "Profesor registrado correctamente.");
      resetProfesorForm();
      closeModal(qs("#profesor-modal"));
      await loadProfesores();
    } catch (error) {
      showMessage("#profesor-message", error.message, true);
      window.alert(error.message);
    }
  });

  qs("#profesor-search").addEventListener("input", debounce(() => loadProfesores()));
  qs("#profesor-estado-filter").addEventListener("change", () => loadProfesores());

  qs("#profesores-table").addEventListener("click", async (event) => {
    const button = event.target.closest("button");
    if (!button) return;
    const viewId = button.dataset.viewProfesor;
    const editId = button.dataset.editProfesor;
    const toggleId = button.dataset.toggleProfesor;
    const deleteId = button.dataset.deleteProfesor;
    if (viewId) {
      const profesor = state.profesores.find((item) => item.id === Number(viewId));
      showProfesorDetail(profesor);
    }
    if (editId) {
      const profesor = state.profesores.find((item) => item.id === Number(editId));
      fillProfesorForm(profesor);
      setText("#profesor-form-title", "Editar Profesor");
      openModal("#profesor-modal");
    }
    if (toggleId) {
      const profesor = state.profesores.find((item) => item.id === Number(toggleId));
      const nextState = !profesor.activo;
      try {
        await api(`/profesores/${toggleId}/estado?activo=${nextState}`, { method: "PATCH" });
        showMessage("#profesor-message", nextState ? "Profesor activado correctamente." : "Profesor desactivado correctamente.");
        await loadProfesores();
      } catch (error) {
        showMessage("#profesor-message", error.message, true);
      }
    }
    if (deleteId && window.confirm("Deseas eliminar este profesor?")) {
      try {
        await api(`/profesores/${deleteId}`, { method: "DELETE" });
        showMessage("#profesor-message", "Profesor eliminado correctamente.");
        await loadProfesores();
      } catch (error) {
        showMessage("#profesor-message", error.message, true);
      }
    }
  });
}

function getAsignaturaFilters() {
  const search = qs("#asignatura-search")?.value.trim() || "";
  const activo = qs("#asignatura-estado-filter")?.value || "";
  const params = new URLSearchParams();
  if (search) params.set("search", search);
  if (activo) params.set("activo", activo);
  return params.toString() ? `?${params.toString()}` : "";
}

async function loadAsignaturas() {
  const query = getAsignaturaFilters();
  const asignaturas = await api(`/asignaturas${query}`);
  const table = qs("#asignaturas-table");
  table.innerHTML = asignaturas
    .map(
      (asignatura) => `
        <tr>
          <td>${asignatura.id}</td>
          <td>${escapeHtml(asignatura.nombre)}</td>
          <td>${escapeHtml(asignatura.codigo)}</td>
          <td>${escapeHtml(asignatura.nivel || "-")}</td>
          <td>${asignatura.horas_semanales || "-"}</td>
          <td><span class="status-badge ${asignatura.activo ? "status-active" : "status-inactive"}">${asignatura.activo ? "Activa" : "Inactiva"}</span></td>
          <td class="actions">
            <button class="button button-light action-button" data-view-asignatura="${asignatura.id}" title="Ver detalle">Ver</button>
            <button class="button button-blue action-button" data-edit-asignatura="${asignatura.id}" title="Editar asignatura">Editar</button>
            <button class="button ${asignatura.activo ? "button-light" : "button-green"} action-button" data-toggle-asignatura="${asignatura.id}" title="${asignatura.activo ? "Desactivar" : "Activar"}">${asignatura.activo ? "Desactivar" : "Activar"}</button>
            <button class="button button-red action-button" data-delete-asignatura="${asignatura.id}" title="Eliminar asignatura">Eliminar</button>
          </td>
        </tr>
      `
    )
    .join("");
  qs("#asignaturas-empty").classList.toggle("hidden", asignaturas.length > 0);
  state.asignaturas = asignaturas;
}

function resetAsignaturaForm() {
  qs("#asignatura-id").value = "";
  qs("#asignatura-form").reset();
  qs("#asignatura-activo").value = "true";
  setText("#asignatura-form-title", "Nueva Asignatura");
}

function fillAsignaturaForm(asignatura) {
  qs("#asignatura-id").value = asignatura.id;
  qs("#asignatura-nombre").value = asignatura.nombre;
  qs("#asignatura-codigo").value = asignatura.codigo;
  qs("#asignatura-nivel").value = asignatura.nivel || "";
  qs("#asignatura-horas").value = asignatura.horas_semanales || "";
  qs("#asignatura-activo").value = String(asignatura.activo);
  qs("#asignatura-descripcion").value = asignatura.descripcion || "";
}

function showAsignaturaDetail(asignatura) {
  qs("#asignatura-detail").innerHTML = `
    <div><span>Asignatura</span><strong>${escapeHtml(asignatura.nombre)}</strong></div>
    <div><span>Codigo</span><strong>${escapeHtml(asignatura.codigo)}</strong></div>
    <div><span>Nivel educativo</span><strong>${escapeHtml(asignatura.nivel || "Sin registrar")}</strong></div>
    <div><span>Horas semanales</span><strong>${asignatura.horas_semanales || "Sin registrar"}</strong></div>
    <div><span>Estado</span><strong>${asignatura.activo ? "Activa" : "Inactiva"}</strong></div>
    <div><span>Descripcion</span><strong>${escapeHtml(asignatura.descripcion || "Sin registrar")}</strong></div>
  `;
  openModal("#asignatura-detail-modal");
}

function bindAsignaturas() {
  qs("#nueva-asignatura").addEventListener("click", () => {
    resetAsignaturaForm();
    openModal("#asignatura-modal");
  });

  qs("#asignatura-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    clearMessage("#asignatura-message");
    const id = qs("#asignatura-id").value;
    const payload = {
      nombre: qs("#asignatura-nombre").value.trim(),
      codigo: qs("#asignatura-codigo").value.trim(),
      nivel: qs("#asignatura-nivel").value.trim() || null,
      horas_semanales: qs("#asignatura-horas").value ? Number(qs("#asignatura-horas").value) : null,
      activo: qs("#asignatura-activo").value === "true",
      descripcion: qs("#asignatura-descripcion").value.trim() || null,
    };
    try {
      await api(id ? `/asignaturas/${id}` : "/asignaturas", {
        method: id ? "PUT" : "POST",
        body: JSON.stringify(payload),
      });
      showMessage("#asignatura-message", id ? "Asignatura actualizada correctamente." : "Asignatura registrada correctamente.");
      resetAsignaturaForm();
      closeModal(qs("#asignatura-modal"));
      await loadAsignaturas();
    } catch (error) {
      showMessage("#asignatura-message", error.message, true);
      window.alert(error.message);
    }
  });

  qs("#asignatura-search").addEventListener("input", debounce(() => loadAsignaturas()));
  qs("#asignatura-estado-filter").addEventListener("change", () => loadAsignaturas());

  qs("#asignaturas-table").addEventListener("click", async (event) => {
    const button = event.target.closest("button");
    if (!button) return;
    const viewId = button.dataset.viewAsignatura;
    const editId = button.dataset.editAsignatura;
    const toggleId = button.dataset.toggleAsignatura;
    const deleteId = button.dataset.deleteAsignatura;
    if (viewId) {
      const asignatura = state.asignaturas.find((item) => item.id === Number(viewId));
      showAsignaturaDetail(asignatura);
    }
    if (editId) {
      const asignatura = state.asignaturas.find((item) => item.id === Number(editId));
      fillAsignaturaForm(asignatura);
      setText("#asignatura-form-title", "Editar Asignatura");
      openModal("#asignatura-modal");
    }
    if (toggleId) {
      const asignatura = state.asignaturas.find((item) => item.id === Number(toggleId));
      const nextState = !asignatura.activo;
      try {
        await api(`/asignaturas/${toggleId}/estado?activo=${nextState}`, { method: "PATCH" });
        showMessage("#asignatura-message", nextState ? "Asignatura activada correctamente." : "Asignatura desactivada correctamente.");
        await loadAsignaturas();
      } catch (error) {
        showMessage("#asignatura-message", error.message, true);
      }
    }
    if (deleteId && window.confirm("Deseas eliminar esta asignatura?")) {
      try {
        await api(`/asignaturas/${deleteId}`, { method: "DELETE" });
        showMessage("#asignatura-message", "Asignatura eliminada correctamente.");
        await loadAsignaturas();
      } catch (error) {
        showMessage("#asignatura-message", error.message, true);
      }
    }
  });
}

async function fillAsignacionSelects() {
  const [profesores, asignaturas] = await Promise.all([api("/profesores?activo=true"), api("/asignaturas?activo=true")]);
  qs("#asignacion-profesor").innerHTML =
    `<option value="">Seleccione un profesor</option>` +
    profesores.map((profesor) => `<option value="${profesor.id}">${profesor.nombre} ${profesor.apellido}</option>`).join("");
  qs("#asignacion-asignatura").innerHTML =
    `<option value="">Seleccione una asignatura</option>` +
    asignaturas.map((asignatura) => `<option value="${asignatura.id}">${asignatura.nombre} (${asignatura.codigo})</option>`).join("");
  const disabled = profesores.length === 0 || asignaturas.length === 0;
  qs("#asignacion-form button").disabled = disabled;
  if (disabled) {
    showMessage("#asignacion-message", "Debes registrar al menos un profesor y una asignatura antes de asignar.", true);
  }
  validateAsignacionSelection();
}

async function loadAsignaciones() {
  const asignaciones = await api("/asignaciones");
  const table = qs("#asignaciones-table");
  table.innerHTML = asignaciones
    .map(
      (asignacion) => `
        <tr>
          <td>${asignacion.id}</td>
          <td>${asignacion.profesor_nombre}</td>
          <td>${asignacion.asignatura_nombre}</td>
          <td>${formatDate(asignacion.fecha_asignacion)}</td>
          <td class="actions">
            <button class="button button-red action-button" data-delete-asignacion="${asignacion.id}" title="Eliminar asignacion">Eliminar</button>
          </td>
        </tr>
      `
    )
    .join("");
  qs("#asignaciones-empty").classList.toggle("hidden", asignaciones.length > 0);
  state.asignaciones = asignaciones;
  validateAsignacionSelection();
}

function validateAsignacionSelection() {
  const submitButton = qs("#asignacion-form button");
  const profesorId = Number(qs("#asignacion-profesor")?.value);
  const asignaturaId = Number(qs("#asignacion-asignatura")?.value);
  if (!submitButton || !profesorId || !asignaturaId) return;

  const exists = state.asignaciones.some(
    (asignacion) => asignacion.profesor_id === profesorId && asignacion.asignatura_id === asignaturaId
  );
  submitButton.disabled = exists;
  if (exists) {
    showMessage("#asignacion-message", "Esta asignatura ya esta asignada a ese profesor. Elige otra combinacion.", true);
  } else {
    clearMessage("#asignacion-message");
  }
}

function bindAsignaciones() {
  qs("#ver-todas-asignaciones")?.addEventListener("click", () => loadAsignaciones());
  qs("#asignacion-profesor").addEventListener("change", validateAsignacionSelection);
  qs("#asignacion-asignatura").addEventListener("change", validateAsignacionSelection);

  qs("#asignacion-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    clearMessage("#asignacion-message");
    const fecha = qs("#asignacion-fecha").value;
    const payload = {
      profesor_id: Number(qs("#asignacion-profesor").value),
      asignatura_id: Number(qs("#asignacion-asignatura").value),
      fecha_asignacion: fecha || null,
    };
    try {
      await api("/asignaciones", { method: "POST", body: JSON.stringify(payload) });
      showMessage("#asignacion-message", "Asignacion registrada correctamente.");
      qs("#asignacion-form").reset();
      await loadAsignaciones();
      validateAsignacionSelection();
    } catch (error) {
      showMessage("#asignacion-message", error.message, true);
    }
  });

  qs("#asignaciones-table").addEventListener("click", async (event) => {
    const deleteId = event.target.dataset.deleteAsignacion;
    if (deleteId && window.confirm("Deseas eliminar esta asignacion?")) {
      try {
        await api(`/asignaciones/${deleteId}`, { method: "DELETE" });
        showMessage("#asignacion-message", "Asignacion eliminada correctamente.");
        await loadAsignaciones();
      } catch (error) {
        showMessage("#asignacion-message", error.message, true);
      }
    }
  });
}

const MONTH_NAMES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];
const WEEKDAYS = ["Lun", "Mar", "Mie", "Jue", "Vie", "Sab", "Dom"];
const EVENT_LABELS = {
  clase: "Clase",
  evaluacion: "Evaluación",
  reunion: "Reunion",
  feriado: "Feriado",
  actividad: "Actividad",
  periodo: "Periodo",
};
const EVENT_CLASS = {
  clase: "class",
  evaluacion: "test",
  reunion: "meeting",
  feriado: "holiday",
  actividad: "activity",
  periodo: "period",
};

function pad2(value) {
  return String(value).padStart(2, "0");
}

function toDateKey(date) {
  return `${date.getFullYear()}-${pad2(date.getMonth() + 1)}-${pad2(date.getDate())}`;
}

function itemDateKey(item) {
  return item.fecha_inicio.slice(0, 10);
}

function formatTime(value) {
  if (!value) return "";
  const date = new Date(value);
  return `${pad2(date.getHours())}:${pad2(date.getMinutes())}`;
}

function formatShortDate(value) {
  const date = new Date(value);
  return `${date.getDate()} ${MONTH_NAMES[date.getMonth()].slice(0, 3)}`;
}

function calendarItemMeta(item) {
  const parts = [];
  if (item.curso_nombre) parts.push(item.curso_nombre);
  if (item.profesor_nombre) parts.push(item.profesor_nombre);
  if (item.asignatura_codigo) parts.push(item.asignatura_codigo);
  return parts.join(" - ");
}

function calendarItemClass(item) {
  return EVENT_CLASS[item.tipo] || "activity";
}

function calendarItemLabel(item) {
  const time = formatTime(item.fecha_inicio);
  const title = item.source === "horario" && item.asignatura_codigo ? item.asignatura_codigo : item.titulo;
  return `${time ? `${time} ` : ""}${title}`;
}

function option(label, value = "", selected = false) {
  return `<option value="${escapeHtml(value)}"${selected ? " selected" : ""}>${escapeHtml(label)}</option>`;
}

function fillSelect(selector, items, labelBuilder, firstLabel, selectedValue = "") {
  const select = qs(selector);
  if (!select) return;
  const normalizedItems = Array.isArray(items) ? items : [];
  const fallbackValue = String(selectedValue || "");
  select.innerHTML =
    option(firstLabel, "", fallbackValue === "") +
    normalizedItems.map((item) => option(labelBuilder(item), item.id, String(item.id) === fallbackValue)).join("");
}

function setCalendarInputsDate() {
  const anio = state.calendario.anio;
  qs("#curso-anio") && (qs("#curso-anio").value = anio);
  qs("#horario-anio") && (qs("#horario-anio").value = anio);
}

function updateCalendarTitle() {
  setText("#calendar-title", `${MONTH_NAMES[state.calendario.mes - 1]} ${state.calendario.anio}`);
  setText("#calendar-subtitle", `Año académico ${state.calendario.anio}`);
  if (qs("#calendar-filter-anio")) qs("#calendar-filter-anio").value = String(state.calendario.anio);
  if (qs("#calendar-filter-mes")) qs("#calendar-filter-mes").value = String(state.calendario.mes);
  setCalendarInputsDate();
}

function calendarParams() {
  const params = new URLSearchParams();
  params.set("anio", state.calendario.anio);
  params.set("mes", state.calendario.mes);
  const tipo = qs("#calendar-filter-tipo")?.value || "";
  const cursoId = qs("#calendar-filter-curso")?.value || "";
  const profesorId = qs("#calendar-filter-profesor")?.value || "";
  const asignaturaId = qs("#calendar-filter-asignatura")?.value || "";
  if (tipo) params.set("tipo", tipo);
  if (cursoId) params.set("curso_id", cursoId);
  if (profesorId) params.set("profesor_id", profesorId);
  if (asignaturaId) params.set("asignatura_id", asignaturaId);
  return params.toString();
}

async function loadCalendarCatalogs() {
  const [cursos, profesores, asignaturas] = await Promise.all([
    api(`/cursos?activo=true&anio_academico=${state.calendario.anio}`),
    api("/profesores?activo=true"),
    api("/asignaturas?activo=true"),
  ]);

  state.calendario.cursos = cursos;
  state.profesores = profesores;
  state.asignaturas = asignaturas;

  fillSelect("#calendar-filter-curso", cursos, (curso) => curso.nombre, "Todos", qs("#calendar-filter-curso")?.value || "");
  fillSelect("#calendar-filter-profesor", profesores, (profesor) => `${profesor.nombre} ${profesor.apellido}`, "Todos", qs("#calendar-filter-profesor")?.value || "");
  fillSelect("#calendar-filter-asignatura", asignaturas, (asignatura) => `${asignatura.nombre} (${asignatura.codigo})`, "Todas", qs("#calendar-filter-asignatura")?.value || "");

  fillSelect("#evento-curso", cursos, (curso) => curso.nombre, "Sin curso");
  fillSelect("#evento-profesor", profesores, (profesor) => `${profesor.nombre} ${profesor.apellido}`, "Sin profesor");
  fillSelect("#evento-asignatura", asignaturas, (asignatura) => `${asignatura.nombre} (${asignatura.codigo})`, "Sin asignatura");

  fillSelect("#horario-curso", cursos, (curso) => curso.nombre, "Seleccione");
  fillSelect("#horario-profesor", profesores, (profesor) => `${profesor.nombre} ${profesor.apellido}`, "Seleccione");
  fillSelect("#horario-asignatura", asignaturas, (asignatura) => `${asignatura.nombre} (${asignatura.codigo})`, "Seleccione");

  const horarioDisabled = cursos.length === 0 || profesores.length === 0 || asignaturas.length === 0;
  qs("#horario-form button") && (qs("#horario-form button").disabled = horarioDisabled);
  if (horarioDisabled) {
    showMessage("#horario-message", "Debes tener curso, profesor y asignatura activos para guardar horarios.", true);
  } else {
    clearMessage("#horario-message");
  }
}

function renderCalendarStats(items) {
  const eventos = items.filter((item) => item.source === "evento").length;
  const clases = items.filter((item) => item.tipo === "clase").length;
  const evaluaciones = items.filter((item) => item.tipo === "evaluacion").length;
  setText("#calendar-total-eventos", eventos);
  setText("#calendar-total-clases", clases);
  setText("#calendar-total-cursos", state.calendario.cursos.length);
  setText("#calendar-total-evaluaciones", evaluaciones);
}

function renderCalendarGrid(items) {
  const grid = qs("#calendar-grid");
  if (!grid) return;

  const year = state.calendario.anio;
  const month = state.calendario.mes;
  const firstDate = new Date(year, month - 1, 1);
  const firstOffset = (firstDate.getDay() + 6) % 7;
  const daysInMonth = new Date(year, month, 0).getDate();
  const totalCells = firstOffset + daysInMonth > 35 ? 42 : 35;
  const todayKey = toDateKey(new Date());

  const byDate = items.reduce((acc, item) => {
    const key = itemDateKey(item);
    acc[key] = acc[key] || [];
    acc[key].push(item);
    return acc;
  }, {});

  const weekdayMarkup = WEEKDAYS.map((day) => `<div class="ordered-weekday">${day}</div>`).join("");
  const dayMarkup = Array.from({ length: totalCells }, (_, index) => {
    const dayNumber = index - firstOffset + 1;
    const cellDate = new Date(year, month - 1, dayNumber);
    const isCurrentMonth = dayNumber >= 1 && dayNumber <= daysInMonth;
    const key = toDateKey(cellDate);
    const dayItems = byDate[key] || [];
    const weekend = cellDate.getDay() === 0 || cellDate.getDay() === 6;
    const important = dayItems.some((item) => ["evaluacion", "periodo", "feriado"].includes(item.tipo));
    const classes = ["ordered-day"];
    if (!isCurrentMonth) classes.push("muted");
    if (weekend) classes.push("weekend");
    if (key === todayKey) classes.push("today");
    if (important) classes.push("important");
    const chips = dayItems
      .slice(0, 3)
      .map((item) => `<span class="ordered-event ${calendarItemClass(item)}" title="${escapeHtml(item.titulo)}">${escapeHtml(calendarItemLabel(item))}</span>`)
      .join("");
    const extra = dayItems.length > 3 ? `<span class="ordered-more">+${dayItems.length - 3} mas</span>` : "";
    return `<div class="${classes.join(" ")}"><strong>${cellDate.getDate()}</strong>${chips}${extra}</div>`;
  }).join("");

  grid.innerHTML = weekdayMarkup + dayMarkup;
  qs("#calendar-empty")?.classList.toggle("hidden", items.length > 0);
}

function renderCalendarAgenda(items) {
  const agenda = qs("#calendar-agenda");
  if (!agenda) return;
  agenda.innerHTML = items.length
    ? items
        .map((item) => {
          const deleteAttr = item.source === "evento" ? `data-delete-evento="${item.source_id}"` : `data-delete-horario="${item.source_id}"`;
          const meta = calendarItemMeta(item) || EVENT_LABELS[item.tipo] || "Evento";
          return `
            <article>
              <time>${escapeHtml(formatShortDate(item.fecha_inicio))}</time>
              <div>
                <strong>${escapeHtml(item.titulo)}</strong>
                <span>${escapeHtml(formatTime(item.fecha_inicio))}${item.fecha_fin ? ` - ${escapeHtml(formatTime(item.fecha_fin))}` : ""} - ${escapeHtml(meta)}</span>
              </div>
              <button class="button button-red action-button" type="button" ${deleteAttr}>Eliminar</button>
            </article>
          `;
        })
        .join("")
    : `<p class="empty-state">No hay eventos para mostrar.</p>`;
}

async function loadCalendarMonth() {
  updateCalendarTitle();
  const data = await api(`/calendario?${calendarParams()}`);
  state.calendario.items = data.items || [];
  renderCalendarStats(state.calendario.items);
  renderCalendarGrid(state.calendario.items);
  renderCalendarAgenda(state.calendario.items);
}

async function refreshCalendar(loadCatalogs = false) {
  clearMessage("#calendario-message");
  if (loadCatalogs) await loadCalendarCatalogs();
  await loadCalendarMonth();
}

function resetCalendarForms() {
  qs("#curso-form")?.reset();
  qs("#evento-form")?.reset();
  qs("#horario-form")?.reset();
  setCalendarInputsDate();
}

function bindCalendario() {
  qs("#calendar-prev")?.addEventListener("click", async () => {
    state.calendario.mes -= 1;
    if (state.calendario.mes < 1) {
      state.calendario.mes = 12;
      state.calendario.anio -= 1;
    }
    await refreshCalendar(true);
  });

  qs("#calendar-next")?.addEventListener("click", async () => {
    state.calendario.mes += 1;
    if (state.calendario.mes > 12) {
      state.calendario.mes = 1;
      state.calendario.anio += 1;
    }
    await refreshCalendar(true);
  });

  qs("#calendar-today")?.addEventListener("click", async () => {
    state.calendario.anio = 2026;
    state.calendario.mes = 6;
    await refreshCalendar(true);
  });

  qs("#calendar-new-event")?.addEventListener("click", () => {
    qs("#evento-panel")?.scrollIntoView({ behavior: "smooth", block: "start" });
    window.setTimeout(() => qs("#evento-titulo")?.focus(), 250);
  });

  qs("#calendar-toggle-filters")?.addEventListener("click", () => {
    qs("#calendar-filter-panel")?.classList.toggle("hidden");
  });

  qs("#calendar-filter-anio")?.addEventListener("change", async (event) => {
    state.calendario.anio = Number(event.target.value);
    await refreshCalendar(true);
  });

  qs("#calendar-filter-mes")?.addEventListener("change", async (event) => {
    state.calendario.mes = Number(event.target.value);
    await refreshCalendar();
  });

  ["#calendar-filter-tipo", "#calendar-filter-curso", "#calendar-filter-profesor", "#calendar-filter-asignatura"].forEach((selector) => {
    qs(selector)?.addEventListener("change", () => refreshCalendar());
  });

  qs("#curso-form")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearMessage("#curso-message");
    const payload = {
      nombre: qs("#curso-nombre").value.trim(),
      nivel: qs("#curso-nivel").value.trim(),
      letra: qs("#curso-letra").value.trim() || null,
      jornada: qs("#curso-jornada").value,
      anio_academico: Number(qs("#curso-anio").value || 2026),
      activo: true,
    };
    try {
      await api("/cursos", { method: "POST", body: JSON.stringify(payload) });
      showMessage("#curso-message", "Curso guardado correctamente.");
      qs("#curso-form").reset();
      setCalendarInputsDate();
      await refreshCalendar(true);
    } catch (error) {
      showMessage("#curso-message", error.message, true);
    }
  });

  qs("#evento-form")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearMessage("#evento-message");
    const payload = {
      titulo: qs("#evento-titulo").value.trim(),
      descripcion: qs("#evento-descripcion").value.trim() || null,
      fecha_inicio: qs("#evento-fecha-inicio").value,
      fecha_fin: qs("#evento-fecha-fin").value || null,
      tipo: qs("#evento-tipo").value,
      curso_id: qs("#evento-curso").value ? Number(qs("#evento-curso").value) : null,
      profesor_id: qs("#evento-profesor").value ? Number(qs("#evento-profesor").value) : null,
      asignatura_id: qs("#evento-asignatura").value ? Number(qs("#evento-asignatura").value) : null,
      anio_academico: state.calendario.anio,
      estado: "activo",
    };
    try {
      await api("/calendario/eventos", { method: "POST", body: JSON.stringify(payload) });
      showMessage("#evento-message", "Evento guardado correctamente.");
      qs("#evento-form").reset();
      await refreshCalendar();
    } catch (error) {
      showMessage("#evento-message", error.message, true);
    }
  });

  qs("#horario-form")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearMessage("#horario-message");
    const payload = {
      curso_id: Number(qs("#horario-curso").value),
      profesor_id: Number(qs("#horario-profesor").value),
      asignatura_id: Number(qs("#horario-asignatura").value),
      dia_semana: Number(qs("#horario-dia").value),
      hora_inicio: qs("#horario-inicio").value,
      hora_fin: qs("#horario-fin").value,
      anio_academico: Number(qs("#horario-anio").value || state.calendario.anio),
      activo: true,
    };
    try {
      await api("/calendario/horarios", { method: "POST", body: JSON.stringify(payload) });
      showMessage("#horario-message", "Horario guardado correctamente.");
      qs("#horario-form").reset();
      setCalendarInputsDate();
      await refreshCalendar();
    } catch (error) {
      showMessage("#horario-message", error.message, true);
    }
  });

  qs("#calendar-agenda")?.addEventListener("click", async (event) => {
    const button = event.target.closest("button");
    if (!button) return;
    const eventoId = button.dataset.deleteEvento;
    const horarioId = button.dataset.deleteHorario;
    if (eventoId && window.confirm("Deseas eliminar este evento?")) {
      try {
        await api(`/calendario/eventos/${eventoId}`, { method: "DELETE" });
        showMessage("#calendario-message", "Evento eliminado correctamente.");
        await refreshCalendar();
      } catch (error) {
        showMessage("#calendario-message", error.message, true);
      }
    }
    if (horarioId && window.confirm("Deseas eliminar este horario semanal?")) {
      try {
        await api(`/calendario/horarios/${horarioId}`, { method: "DELETE" });
        showMessage("#calendario-message", "Horario eliminado correctamente.");
        await refreshCalendar();
      } catch (error) {
        showMessage("#calendario-message", error.message, true);
      }
    }
  });
}

async function initCalendario() {
  bindCalendario();
  resetCalendarForms();
  await refreshCalendar(true);
}

function notasAnio() {
  return Number(qs("#nota-filter-anio")?.value || state.notas.anio || 2026);
}

function notasFilters() {
  const params = new URLSearchParams();
  params.set("anio_academico", notasAnio());
  const cursoId = qs("#nota-filter-curso")?.value || "";
  const asignaturaId = qs("#nota-filter-asignatura")?.value || "";
  const profesorId = qs("#nota-filter-profesor")?.value || "";
  const periodoId = qs("#nota-filter-periodo")?.value || "";
  if (cursoId) params.set("curso_id", cursoId);
  if (asignaturaId) params.set("asignatura_id", asignaturaId);
  if (profesorId) params.set("profesor_id", profesorId);
  if (periodoId) params.set("periodo_id", periodoId);
  return params.toString();
}

function formatNota(value) {
  return value === null || value === undefined ? "-" : Number(value).toFixed(1);
}

function notaEstado(promedio) {
  if (promedio === null || promedio === undefined) return { label: "Sin notas", ok: false };
  return promedio >= 5.5 ? { label: "Aprobado", ok: true } : { label: "Reprobado", ok: false };
}

function weightedAverage(notas) {
  const valid = notas.filter((item) => item.nota !== null && item.nota !== undefined && item.ponderacion > 0);
  const totalWeight = valid.reduce((sum, item) => sum + item.ponderacion, 0);
  if (!totalWeight) return null;
  return valid.reduce((sum, item) => sum + Number(item.nota) * item.ponderacion, 0) / totalWeight;
}

function gradebookParams() {
  const params = new URLSearchParams();
  params.set("anio_academico", notasAnio());
  const cursoId = qs("#gradebook-curso")?.value || qs("#nota-filter-curso")?.value || "";
  const asignaturaId = qs("#gradebook-asignatura")?.value || qs("#nota-filter-asignatura")?.value || "";
  const profesorId = qs("#gradebook-profesor")?.value || qs("#nota-filter-profesor")?.value || "";
  if (cursoId) params.set("curso_id", cursoId);
  if (asignaturaId) params.set("asignatura_id", asignaturaId);
  if (profesorId) params.set("profesor_id", profesorId);
  return params;
}

async function loadNotasCatalogs() {
  const anio = notasAnio();
  state.notas.anio = anio;
  const [cursos, profesores, asignaturas, periodos] = await Promise.all([
    api(`/cursos?activo=true&anio_academico=${anio}`),
    api("/profesores?activo=true"),
    api("/asignaturas?activo=true"),
    api(`/periodos?anio_academico=${anio}`),
  ]);
  state.calendario.cursos = cursos;
  state.profesores = profesores;
  state.asignaturas = asignaturas;
  state.notas.periodos = periodos;

  const selectedCurso = qs("#gradebook-curso")?.value || qs("#nota-filter-curso")?.value || cursos[0]?.id || "";
  fillSelect("#nota-filter-curso", cursos, (curso) => curso.nombre, "Todos", qs("#nota-filter-curso")?.value || "");
  fillSelect("#nota-filter-asignatura", asignaturas, (asignatura) => `${asignatura.nombre} (${asignatura.codigo})`, "Todas", qs("#nota-filter-asignatura")?.value || "");
  fillSelect("#nota-filter-profesor", profesores, (profesor) => `${profesor.nombre} ${profesor.apellido}`, "Todos", qs("#nota-filter-profesor")?.value || "");
  fillSelect("#nota-filter-periodo", periodos, (periodo) => periodo.nombre, "Todos", qs("#nota-filter-periodo")?.value || "");

  fillSelect("#gradebook-curso", cursos, (curso) => curso.nombre, "Seleccione curso", selectedCurso);
  fillSelect("#gradebook-asignatura", asignaturas, (asignatura) => asignatura.nombre, "Todas", qs("#gradebook-asignatura")?.value || qs("#nota-filter-asignatura")?.value || "");
  fillSelect("#gradebook-profesor", profesores, (profesor) => `${profesor.nombre} ${profesor.apellido}`, "Todos", qs("#gradebook-profesor")?.value || qs("#nota-filter-profesor")?.value || "");

  fillSelect("#estudiante-curso", cursos, (curso) => curso.nombre, "Seleccione", qs("#estudiante-curso")?.value || selectedCurso);
  fillSelect("#evaluacion-curso", cursos, (curso) => curso.nombre, "Seleccione", qs("#evaluacion-curso")?.value || selectedCurso);
  fillSelect("#evaluacion-asignatura", asignaturas, (asignatura) => `${asignatura.nombre} (${asignatura.codigo})`, "Seleccione");
  fillSelect("#evaluacion-profesor", profesores, (profesor) => `${profesor.nombre} ${profesor.apellido}`, "Seleccione");
  fillSelect("#evaluacion-periodo", periodos.filter((periodo) => periodo.activo), (periodo) => periodo.nombre, "Seleccione");

  ["#estudiante-anio", "#periodo-anio"].forEach((selector) => {
    if (qs(selector)) qs(selector).value = anio;
  });
}

async function loadEstudiantesNotas() {
  const params = new URLSearchParams();
  params.set("anio_academico", notasAnio());
  const cursoId = qs("#nota-filter-curso")?.value || "";
  if (cursoId) params.set("curso_id", cursoId);
  const estudiantes = await api(`/estudiantes?${params.toString()}`);
  state.notas.estudiantes = estudiantes;
  renderEstudiantesTable(estudiantes);
}

function renderEstudiantesTable(estudiantes) {
  const table = qs("#estudiantes-table");
  if (!table) return;
  table.innerHTML = estudiantes
    .map(
      (estudiante) => `
        <tr>
          <td>
            <strong>${escapeHtml(estudiante.nombre)} ${escapeHtml(estudiante.apellido)}</strong>
            <span class="muted-line">${escapeHtml(estudiante.rut || estudiante.correo || "Sin identificador")}</span>
          </td>
          <td>${escapeHtml(estudiante.curso_nombre || "-")}</td>
          <td><span class="status-badge ${estudiante.activo ? "status-active" : "status-inactive"}">${estudiante.activo ? "Activo" : "Inactivo"}</span></td>
          <td class="actions">
            <a class="button button-light action-button" href="perfil-estudiante.html?id=${estudiante.id}">Perfil</a>
            <button class="button button-blue action-button" type="button" data-edit-estudiante="${estudiante.id}">Editar</button>
            <button class="button ${estudiante.activo ? "button-light" : "button-green"} action-button" type="button" data-toggle-estudiante="${estudiante.id}">${estudiante.activo ? "Desactivar" : "Activar"}</button>
            <button class="button button-red action-button" type="button" data-delete-estudiante="${estudiante.id}">Eliminar</button>
          </td>
        </tr>
      `
    )
    .join("");
  qs("#estudiantes-empty")?.classList.toggle("hidden", estudiantes.length > 0);
}

function renderPeriodosTable(periodos) {
  const table = qs("#periodos-table");
  if (!table) return;
  table.innerHTML = periodos
    .map(
      (periodo) => `
        <tr>
          <td><strong>${escapeHtml(periodo.nombre)}</strong><span class="muted-line">Año ${periodo.anio_academico}</span></td>
          <td>${escapeHtml(formatDate(periodo.fecha_inicio))} - ${escapeHtml(formatDate(periodo.fecha_fin))}</td>
          <td><span class="status-badge ${periodo.activo ? "status-active" : "status-inactive"}">${periodo.activo ? "Activo" : "Inactivo"}</span></td>
          <td class="actions">
            <button class="button button-blue action-button" type="button" data-edit-periodo="${periodo.id}">Editar</button>
            <button class="button ${periodo.activo ? "button-light" : "button-green"} action-button" type="button" data-toggle-periodo="${periodo.id}">${periodo.activo ? "Desactivar" : "Activar"}</button>
            <button class="button button-red action-button" type="button" data-delete-periodo="${periodo.id}">Eliminar</button>
          </td>
        </tr>
      `
    )
    .join("");
  qs("#periodos-empty")?.classList.toggle("hidden", periodos.length > 0);
}

async function loadNotasDashboardStats() {
  const resumen = await api("/dashboard/resumen");
  setText("#notas-total-estudiantes", resumen.total_estudiantes || 0);
  setText("#notas-total-evaluaciones", resumen.total_evaluaciones || 0);
  setText("#notas-total-notas", resumen.total_notas || 0);
  setText("#notas-promedio-general", resumen.promedio_general ? Number(resumen.promedio_general).toFixed(1) : "-");
}

async function renderGradebook() {
  const head = qs("#gradebook-head");
  const body = qs("#gradebook-body");
  const empty = qs("#gradebook-empty");
  if (!head || !body || !empty) return;

  const params = gradebookParams();
  const cursoId = params.get("curso_id");
  if (!cursoId) {
    head.innerHTML = "";
    body.innerHTML = "";
    empty.textContent = "Selecciona un curso para ver el libro de notas.";
    empty.classList.remove("hidden");
    renderGradebookSummary([]);
    return;
  }

  const [estudiantes, evaluaciones, notas] = await Promise.all([
    api(`/estudiantes?activo=true&curso_id=${cursoId}&anio_academico=${notasAnio()}`),
    api(`/evaluaciones?${params.toString()}`),
    api(`/notas?${params.toString()}`),
  ]);
  const visibles = evaluaciones.filter((evaluacion) => evaluacion.estado !== "cancelada").slice(0, 6);
  state.notas.gradeEvaluaciones = visibles;
  const notasByKey = new Map(notas.map((nota) => [`${nota.estudiante_id}-${nota.evaluacion_id}`, nota]));
  const gradeRows = [];

  head.innerHTML = `
    <tr>
      <th>#</th>
      <th>Alumno</th>
      ${visibles.map((evaluacion, index) => `<th>Nota ${index + 1}<span>${escapeHtml(evaluacion.titulo)}</span></th>`).join("")}
      <th>Promedio Final</th>
      <th>Estado</th>
    </tr>
  `;

  body.innerHTML = estudiantes
    .map((estudiante, index) => {
      const studentNotas = visibles.map((evaluacion) => {
        const registro = notasByKey.get(`${estudiante.id}-${evaluacion.id}`);
        return {
          evaluacion,
          registro,
          nota: registro ? Number(registro.nota) : null,
          ponderacion: Number(evaluacion.ponderacion || 0),
        };
      });
      const promedio = weightedAverage(studentNotas);
      const estado = notaEstado(promedio);
      gradeRows.push({ estudiante, promedio, estado, notas: studentNotas });
      return `
        <tr>
          <td>${index + 1}</td>
          <td>${escapeHtml(estudiante.nombre)} ${escapeHtml(estudiante.apellido)}</td>
          ${studentNotas
            .map(
              ({ evaluacion, registro, nota }) => `
                <td>
                  <input class="gradebook-input" type="number" min="1" max="7" step="0.1"
                    data-grade-estudiante="${estudiante.id}"
                    data-grade-evaluacion="${evaluacion.id}"
                    data-grade-nota="${registro?.id || ""}"
                    value="${nota === null ? "" : Number(nota).toFixed(1)}">
                </td>
              `
            )
            .join("")}
          <td><strong class="gradebook-average">${promedio === null ? "-" : promedio.toFixed(2)}</strong></td>
          <td><span class="grade-status ${estado.ok ? "approved" : "failed"}">${estado.label}</span></td>
        </tr>
      `;
    })
    .join("");

  empty.textContent = estudiantes.length && visibles.length ? "" : "Este curso no tiene estudiantes o evaluaciones para mostrar.";
  empty.classList.toggle("hidden", estudiantes.length > 0 && visibles.length > 0);
  state.notas.gradeRows = gradeRows;
  renderGradebookSummary(gradeRows);
}

function renderGradebookSummary(rows) {
  const averages = rows.map((row) => row.promedio).filter((value) => value !== null && value !== undefined);
  const allNotas = rows.flatMap((row) => row.notas.map((item) => item.nota)).filter((value) => value !== null && value !== undefined);
  const general = averages.length ? averages.reduce((sum, value) => sum + value, 0) / averages.length : null;
  const max = allNotas.length ? Math.max(...allNotas) : null;
  const min = allNotas.length ? Math.min(...allNotas) : null;
  const approved = rows.filter((row) => row.promedio !== null && row.promedio >= 5.5).length;

  setText("#gradebook-promedio", general === null ? "-" : general.toFixed(2));
  setText("#gradebook-maxima", max === null ? "-" : max.toFixed(1));
  setText("#gradebook-minima", min === null ? "-" : min.toFixed(1));
  setText("#gradebook-aprobados", `${approved} / ${rows.length}`);

  const high = averages.filter((value) => value >= 6).length;
  const mid = averages.filter((value) => value >= 5 && value < 6).length;
  const low = averages.filter((value) => value >= 4 && value < 5).length;
  const veryLow = averages.filter((value) => value < 4).length;
  const total = Math.max(averages.length, 1);
  const highPct = Math.round((high / total) * 100);
  const midPct = Math.round((mid / total) * 100);
  const lowPct = Math.round((low / total) * 100);
  const veryLowPct = Math.max(0, 100 - highPct - midPct - lowPct);
  const donut = qs("#gradebook-donut");
  if (donut) {
    donut.style.background = `conic-gradient(#68b76f 0 ${highPct}%, #4a7fe3 ${highPct}% ${highPct + midPct}%, #ffbd1a ${highPct + midPct}% ${highPct + midPct + lowPct}%, #ef4444 ${highPct + midPct + lowPct}% 100%)`;
  }
  const legend = qs("#gradebook-distribution");
  if (legend) {
    legend.innerHTML = [
      ["green", "7.0 - 6.0", highPct, high],
      ["blue", "5.9 - 5.0", midPct, mid],
      ["yellow", "4.9 - 4.0", lowPct, low],
      ["red", "3.9 - 1.0", veryLowPct, veryLow],
    ]
      .map(([color, label, pct, count]) => `<span><i class="${color}"></i>${label}<strong>${pct}% (${count})</strong></span>`)
      .join("");
  }
}

async function saveGradebookNotas() {
  const inputs = qsa(".gradebook-input");
  let saved = 0;
  for (const input of inputs) {
    const value = input.value.trim();
    const notaId = input.dataset.gradeNota;
    if (!value && notaId) {
      await api(`/notas/${notaId}`, { method: "DELETE" });
      saved += 1;
      continue;
    }
    if (!value) continue;
    const nota = Number(value);
    if (Number.isNaN(nota) || nota < 1 || nota > 7 || Math.round(nota * 10) !== nota * 10) {
      throw new Error("Todas las notas deben estar entre 1.0 y 7.0, con maximo un decimal.");
    }
    await api("/notas", {
      method: "POST",
      body: JSON.stringify({
        estudiante_id: Number(input.dataset.gradeEstudiante),
        evaluacion_id: Number(input.dataset.gradeEvaluacion),
        nota,
        observacion: null,
      }),
    });
    saved += 1;
  }
  return saved;
}

function exportGradebookCsv() {
  const rows = [["Alumno", ...(state.notas.gradeEvaluaciones || []).map((item) => item.titulo), "Promedio", "Estado"]];
  (state.notas.gradeRows || []).forEach((row) => {
    rows.push([
      `${row.estudiante.nombre} ${row.estudiante.apellido}`,
      ...row.notas.map((item) => (item.nota === null ? "" : Number(item.nota).toFixed(1))),
      row.promedio === null ? "" : row.promedio.toFixed(2),
      row.estado.label,
    ]);
  });
  const csv = rows.map((row) => row.map((cell) => `"${String(cell).replaceAll('"', '""')}"`).join(";")).join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `notas-${new Date().toISOString().slice(0, 10)}.csv`;
  link.click();
  URL.revokeObjectURL(url);
}

async function loadEvaluacionesNotas() {
  const evaluaciones = await api(`/evaluaciones?${notasFilters()}`);
  state.notas.evaluaciones = evaluaciones;
  const selected = qs("#nota-evaluacion-select")?.value || "";
  const selectedExists = evaluaciones.some((evaluacion) => String(evaluacion.id) === String(selected));
  fillSelect(
    "#nota-evaluacion-select",
    evaluaciones,
    (evaluacion) => `${evaluacion.titulo} - ${evaluacion.curso_nombre || ""} - ${evaluacion.asignatura_nombre || ""}`,
    "Seleccione evaluación",
    selectedExists ? selected : ""
  );
  renderEvaluacionesTable(evaluaciones);
}

function renderEvaluacionesTable(evaluaciones) {
  const table = qs("#evaluaciones-table");
  if (!table) return;
  table.innerHTML = evaluaciones
    .map((evaluacion) => {
      const nextPrimary = evaluacion.estado === "activa" ? "cerrada" : "activa";
      const nextLabel = evaluacion.estado === "activa" ? "Cerrar" : "Activar";
      return `
        <tr>
          <td>
            <strong>${escapeHtml(evaluacion.titulo)}</strong>
            <span class="muted-line">${escapeHtml(evaluacion.asignatura_nombre || "-")} - ${escapeHtml(formatDate(evaluacion.fecha))}</span>
          </td>
          <td>${escapeHtml(evaluacion.curso_nombre || "-")}</td>
          <td>${Number(evaluacion.ponderacion).toFixed(2)}%</td>
          <td><span class="status-badge ${evaluacion.estado === "activa" ? "status-active" : "status-inactive"}">${escapeHtml(evaluacion.estado)}</span></td>
          <td class="actions">
            <button class="button button-blue action-button" type="button" data-edit-evaluacion="${evaluacion.id}">Editar</button>
            <button class="button button-light action-button" type="button" data-estado-evaluacion="${evaluacion.id}" data-next-estado="${nextPrimary}">${nextLabel}</button>
            <button class="button button-light action-button" type="button" data-estado-evaluacion="${evaluacion.id}" data-next-estado="cancelada">Cancelar</button>
            <button class="button button-red action-button" type="button" data-delete-evaluacion="${evaluacion.id}">Eliminar</button>
          </td>
        </tr>
      `;
    })
    .join("");
  qs("#evaluaciones-empty")?.classList.toggle("hidden", evaluaciones.length > 0);
}

async function loadNotasResumen() {
  const resumen = await api(`/notas/resumen?${notasFilters()}`);
  state.notas.resumen = resumen.items || [];
  setText("#notas-promedio-general", resumen.promedio_general ? Number(resumen.promedio_general).toFixed(1) : "-");
  const table = qs("#nota-resumen-table");
  if (!table) return;
  table.innerHTML = state.notas.resumen
    .map(
      (item) => `
        <tr>
          <td>${escapeHtml(item.estudiante_nombre)}</td>
          <td>${escapeHtml(item.curso_nombre)}</td>
          <td>${escapeHtml(item.asignatura_nombre)}</td>
          <td><strong>${formatNota(item.promedio)}</strong></td>
        </tr>
      `
    )
    .join("");
  qs("#nota-resumen-empty")?.classList.toggle("hidden", state.notas.resumen.length > 0);
}

async function renderIngresoNotas() {
  const evaluacionId = Number(qs("#nota-evaluacion-select")?.value || 0);
  const table = qs("#nota-ingreso-table");
  const empty = qs("#nota-ingreso-empty");
  if (!table || !empty) return;
  if (!evaluacionId) {
    table.innerHTML = "";
    empty.textContent = "Seleccione una evaluación para ingresar notas.";
    empty.classList.remove("hidden");
    return;
  }

  const evaluacion = state.notas.evaluaciones.find((item) => item.id === evaluacionId) || await api(`/evaluaciones/${evaluacionId}`);
  const [estudiantes, notas] = await Promise.all([
    api(`/estudiantes?activo=true&curso_id=${evaluacion.curso_id}&anio_academico=${evaluacion.anio_academico}`),
    api(`/notas?evaluacion_id=${evaluacionId}`),
  ]);
  state.notas.ingresoEstudiantes = estudiantes;
  state.notas.registros = notas;
  table.innerHTML = estudiantes
    .map((estudiante) => {
      const registro = notas.find((nota) => nota.estudiante_id === estudiante.id);
      return `
        <tr data-estudiante-id="${estudiante.id}">
          <td>${escapeHtml(estudiante.nombre)} ${escapeHtml(estudiante.apellido)}</td>
          <td><input class="nota-input" type="number" min="1" max="7" step="0.1" value="${registro ? Number(registro.nota).toFixed(1) : ""}" placeholder="1.0 - 7.0"></td>
          <td><input class="nota-observacion" value="${escapeHtml(registro?.observacion || "")}" placeholder="Observacion opcional"></td>
          <td class="actions">
            <button class="button button-blue action-button" type="button" data-save-nota="${estudiante.id}">Guardar</button>
            ${registro ? `<button class="button button-red action-button" type="button" data-delete-nota="${registro.id}">Eliminar</button>` : ""}
          </td>
        </tr>
      `;
    })
    .join("");
  empty.textContent = estudiantes.length ? "" : "No hay estudiantes activos en el curso de esta evaluación.";
  empty.classList.toggle("hidden", estudiantes.length > 0);
}

async function refreshNotas(loadCatalogs = false) {
  clearMessage("#notas-message");
  if (loadCatalogs) {
    await loadNotasCatalogs();
    renderPeriodosTable(state.notas.periodos);
  }
  await Promise.all([loadNotasDashboardStats(), loadEstudiantesNotas(), loadEvaluacionesNotas(), loadNotasResumen()]);
  await renderGradebook();
  await renderIngresoNotas();
}

function resetEstudianteForm() {
  qs("#estudiante-id").value = "";
  qs("#estudiante-form")?.reset();
  qs("#estudiante-anio").value = notasAnio();
  setText("#estudiante-form-title", "Nuevo estudiante");
}

function fillEstudianteForm(estudiante) {
  qs("#estudiante-id").value = estudiante.id;
  qs("#estudiante-rut").value = estudiante.rut || "";
  qs("#estudiante-nombre").value = estudiante.nombre;
  qs("#estudiante-apellido").value = estudiante.apellido;
  qs("#estudiante-correo").value = estudiante.correo || "";
  qs("#estudiante-curso").value = estudiante.curso_id;
  qs("#estudiante-anio").value = estudiante.anio_academico;
  setText("#estudiante-form-title", "Editar estudiante");
  qs("#estudiante-form")?.scrollIntoView({ behavior: "smooth", block: "start" });
}

function resetPeriodoForm() {
  qs("#periodo-id").value = "";
  qs("#periodo-form")?.reset();
  qs("#periodo-anio").value = notasAnio();
  setText("#periodo-form-title", "Nuevo periodo");
}

function fillPeriodoForm(periodo) {
  qs("#periodo-id").value = periodo.id;
  qs("#periodo-nombre").value = periodo.nombre;
  qs("#periodo-inicio").value = periodo.fecha_inicio;
  qs("#periodo-fin").value = periodo.fecha_fin;
  qs("#periodo-anio").value = periodo.anio_academico;
  setText("#periodo-form-title", "Editar periodo");
  qs("#periodo-form")?.scrollIntoView({ behavior: "smooth", block: "start" });
}

function resetEvaluacionForm() {
  qs("#evaluacion-id").value = "";
  qs("#evaluacion-form")?.reset();
  qs("#evaluacion-ponderacion").value = "10";
  qs("#evaluacion-estado").value = "activa";
  setText("#evaluacion-form-title", "Nueva evaluación");
}

function fillEvaluacionForm(evaluacion) {
  qs("#evaluacion-id").value = evaluacion.id;
  qs("#evaluacion-titulo").value = evaluacion.titulo;
  qs("#evaluacion-curso").value = evaluacion.curso_id;
  qs("#evaluacion-asignatura").value = evaluacion.asignatura_id;
  qs("#evaluacion-profesor").value = evaluacion.profesor_id;
  qs("#evaluacion-periodo").value = evaluacion.periodo_id;
  qs("#evaluacion-fecha").value = evaluacion.fecha;
  qs("#evaluacion-ponderacion").value = evaluacion.ponderacion;
  qs("#evaluacion-estado").value = evaluacion.estado;
  qs("#evaluacion-descripcion").value = evaluacion.descripcion || "";
  setText("#evaluacion-form-title", "Editar evaluación");
  qs("#evaluacion-form")?.scrollIntoView({ behavior: "smooth", block: "start" });
}

function bindNotas() {
  qs("#estudiante-cancelar")?.addEventListener("click", resetEstudianteForm);
  qs("#periodo-cancelar")?.addEventListener("click", resetPeriodoForm);
  qs("#evaluacion-cancelar")?.addEventListener("click", resetEvaluacionForm);

  qs("#estudiante-form")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearMessage("#estudiante-message");
    const id = qs("#estudiante-id").value;
    const payload = {
      rut: qs("#estudiante-rut").value.trim() || null,
      nombre: qs("#estudiante-nombre").value.trim(),
      apellido: qs("#estudiante-apellido").value.trim(),
      correo: qs("#estudiante-correo").value.trim() || null,
      curso_id: Number(qs("#estudiante-curso").value),
      anio_academico: Number(qs("#estudiante-anio").value || notasAnio()),
      activo: true,
    };
    try {
      await api(id ? `/estudiantes/${id}` : "/estudiantes", { method: id ? "PUT" : "POST", body: JSON.stringify(payload) });
      showMessage("#estudiante-message", id ? "Estudiante actualizado correctamente." : "Estudiante guardado correctamente.");
      resetEstudianteForm();
      await refreshNotas(true);
    } catch (error) {
      showMessage("#estudiante-message", error.message, true);
    }
  });

  qs("#periodo-form")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearMessage("#periodo-message");
    const id = qs("#periodo-id").value;
    const payload = {
      nombre: qs("#periodo-nombre").value.trim(),
      fecha_inicio: qs("#periodo-inicio").value,
      fecha_fin: qs("#periodo-fin").value,
      anio_academico: Number(qs("#periodo-anio").value || notasAnio()),
      activo: true,
    };
    try {
      await api(id ? `/periodos/${id}` : "/periodos", { method: id ? "PUT" : "POST", body: JSON.stringify(payload) });
      showMessage("#periodo-message", id ? "Periodo actualizado correctamente." : "Periodo guardado correctamente.");
      resetPeriodoForm();
      await refreshNotas(true);
    } catch (error) {
      showMessage("#periodo-message", error.message, true);
    }
  });

  qs("#evaluacion-form")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearMessage("#evaluacion-message");
    const id = qs("#evaluacion-id").value;
    const payload = {
      titulo: qs("#evaluacion-titulo").value.trim(),
      descripcion: qs("#evaluacion-descripcion").value.trim() || null,
      curso_id: Number(qs("#evaluacion-curso").value),
      asignatura_id: Number(qs("#evaluacion-asignatura").value),
      profesor_id: Number(qs("#evaluacion-profesor").value),
      periodo_id: Number(qs("#evaluacion-periodo").value),
      fecha: qs("#evaluacion-fecha").value,
      ponderacion: Number(qs("#evaluacion-ponderacion").value),
      anio_academico: notasAnio(),
      estado: qs("#evaluacion-estado").value,
    };
    try {
      await api(id ? `/evaluaciones/${id}` : "/evaluaciones", { method: id ? "PUT" : "POST", body: JSON.stringify(payload) });
      showMessage("#evaluacion-message", id ? "Evaluación actualizada correctamente." : "Evaluación guardada correctamente.");
      resetEvaluacionForm();
      await refreshNotas();
    } catch (error) {
      showMessage("#evaluacion-message", error.message, true);
    }
  });

  qs("#nota-evaluacion-select")?.addEventListener("change", renderIngresoNotas);

  ["#nota-filter-curso", "#nota-filter-asignatura", "#nota-filter-profesor", "#nota-filter-periodo"].forEach((selector) => {
    qs(selector)?.addEventListener("change", () => refreshNotas());
  });

  qs("#nota-filter-anio")?.addEventListener("change", () => refreshNotas(true));

  qs("#gradebook-filtrar")?.addEventListener("click", async () => {
    if (qs("#nota-filter-curso")) qs("#nota-filter-curso").value = qs("#gradebook-curso").value;
    if (qs("#nota-filter-asignatura")) qs("#nota-filter-asignatura").value = qs("#gradebook-asignatura").value;
    if (qs("#nota-filter-profesor")) qs("#nota-filter-profesor").value = qs("#gradebook-profesor").value;
    await refreshNotas();
  });

  ["#gradebook-curso", "#gradebook-asignatura", "#gradebook-profesor"].forEach((selector) => {
    qs(selector)?.addEventListener("change", () => qs("#gradebook-filtrar")?.click());
  });

  qs("#gradebook-guardar")?.addEventListener("click", async () => {
    try {
      const saved = await saveGradebookNotas();
      showMessage("#notas-message", saved ? "Notas guardadas correctamente." : "No hay notas para guardar.");
      await refreshNotas();
    } catch (error) {
      showMessage("#notas-message", error.message, true);
    }
  });

  qs("#gradebook-exportar")?.addEventListener("click", exportGradebookCsv);

  qs("#estudiantes-table")?.addEventListener("click", async (event) => {
    const button = event.target.closest("button");
    if (!button) return;
    const editId = button.dataset.editEstudiante;
    const toggleId = button.dataset.toggleEstudiante;
    const deleteId = button.dataset.deleteEstudiante;
    if (editId) {
      const estudiante = state.notas.estudiantes.find((item) => item.id === Number(editId));
      if (estudiante) fillEstudianteForm(estudiante);
    }
    if (toggleId) {
      const estudiante = state.notas.estudiantes.find((item) => item.id === Number(toggleId));
      try {
        await api(`/estudiantes/${toggleId}/estado?activo=${!estudiante.activo}`, { method: "PATCH" });
        showMessage("#notas-message", "Estado del estudiante actualizado.");
        await refreshNotas();
      } catch (error) {
        showMessage("#notas-message", error.message, true);
      }
    }
    if (deleteId && window.confirm("Deseas eliminar este estudiante?")) {
      try {
        await api(`/estudiantes/${deleteId}`, { method: "DELETE" });
        showMessage("#notas-message", "Estudiante eliminado correctamente.");
        resetEstudianteForm();
        await refreshNotas(true);
      } catch (error) {
        showMessage("#notas-message", error.message, true);
      }
    }
  });

  qs("#periodos-table")?.addEventListener("click", async (event) => {
    const button = event.target.closest("button");
    if (!button) return;
    const editId = button.dataset.editPeriodo;
    const toggleId = button.dataset.togglePeriodo;
    const deleteId = button.dataset.deletePeriodo;
    if (editId) {
      const periodo = state.notas.periodos.find((item) => item.id === Number(editId));
      if (periodo) fillPeriodoForm(periodo);
    }
    if (toggleId) {
      const periodo = state.notas.periodos.find((item) => item.id === Number(toggleId));
      try {
        await api(`/periodos/${toggleId}`, { method: "PUT", body: JSON.stringify({ activo: !periodo.activo }) });
        showMessage("#notas-message", "Estado del periodo actualizado.");
        await refreshNotas(true);
      } catch (error) {
        showMessage("#notas-message", error.message, true);
      }
    }
    if (deleteId && window.confirm("Deseas eliminar este periodo?")) {
      try {
        await api(`/periodos/${deleteId}`, { method: "DELETE" });
        showMessage("#notas-message", "Periodo eliminado correctamente.");
        resetPeriodoForm();
        await refreshNotas(true);
      } catch (error) {
        showMessage("#notas-message", error.message, true);
      }
    }
  });

  qs("#evaluaciones-table")?.addEventListener("click", async (event) => {
    const button = event.target.closest("button");
    if (!button) return;
    const editId = button.dataset.editEvaluacion;
    const estadoId = button.dataset.estadoEvaluacion;
    const deleteId = button.dataset.deleteEvaluacion;
    if (editId) {
      const evaluacion = state.notas.evaluaciones.find((item) => item.id === Number(editId));
      if (evaluacion) fillEvaluacionForm(evaluacion);
    }
    if (estadoId) {
      try {
        await api(`/evaluaciones/${estadoId}/estado?estado_evaluacion=${encodeURIComponent(button.dataset.nextEstado)}`, { method: "PATCH" });
        showMessage("#notas-message", "Estado de la evaluación actualizado.");
        await refreshNotas();
      } catch (error) {
        showMessage("#notas-message", error.message, true);
      }
    }
    if (deleteId && window.confirm("Deseas eliminar esta evaluación?")) {
      try {
        await api(`/evaluaciones/${deleteId}`, { method: "DELETE" });
        showMessage("#notas-message", "Evaluación eliminada correctamente.");
        resetEvaluacionForm();
        await refreshNotas();
      } catch (error) {
        showMessage("#notas-message", error.message, true);
      }
    }
  });

  qs("#nota-ingreso-table")?.addEventListener("click", async (event) => {
    const deleteButton = event.target.closest("button[data-delete-nota]");
    if (deleteButton && window.confirm("Deseas eliminar esta nota?")) {
      try {
        await api(`/notas/${deleteButton.dataset.deleteNota}`, { method: "DELETE" });
        showMessage("#notas-message", "Nota eliminada correctamente.");
        await Promise.all([loadNotasDashboardStats(), loadNotasResumen(), renderIngresoNotas()]);
      } catch (error) {
        showMessage("#notas-message", error.message, true);
      }
      return;
    }

    const button = event.target.closest("button[data-save-nota]");
    if (!button) return;
    const row = button.closest("tr");
    const evaluacionId = Number(qs("#nota-evaluacion-select").value);
    const estudianteId = Number(button.dataset.saveNota);
    const notaValue = Number(row.querySelector(".nota-input").value);
    const observacion = row.querySelector(".nota-observacion").value.trim() || null;
    if (!notaValue) {
      showMessage("#notas-message", "Ingresa una nota valida antes de guardar.", true);
      return;
    }
    try {
      await api("/notas", {
        method: "POST",
        body: JSON.stringify({
          estudiante_id: estudianteId,
          evaluacion_id: evaluacionId,
          nota: notaValue,
          observacion,
        }),
      });
      showMessage("#notas-message", "Nota guardada correctamente.");
      await Promise.all([loadNotasDashboardStats(), loadNotasResumen(), renderIngresoNotas()]);
    } catch (error) {
      showMessage("#notas-message", error.message, true);
    }
  });
}

async function initNotas() {
  bindNotas();
  resetEstudianteForm();
  resetPeriodoForm();
  resetEvaluacionForm();
  await refreshNotas(true);
}

function asistenciaAnio() {
  return Number(qs("#asistencia-anio")?.value || state.asistencia.anio || 2026);
}

function asistenciaFecha() {
  return qs("#asistencia-fecha")?.value || new Date().toISOString().slice(0, 10);
}

function asistenciaCursoId() {
  return Number(qs("#asistencia-curso")?.value || 0);
}

function asistenciaStatusOptions(selected = "presente") {
  return [
    ["presente", "Presente"],
    ["ausente", "Ausente"],
    ["tarde", "Tarde"],
    ["justificado", "Justificado"],
  ]
    .map(([value, label]) => `<option value="${value}" ${value === selected ? "selected" : ""}>${label}</option>`)
    .join("");
}

async function loadAsistenciaCatalogs() {
  const anio = asistenciaAnio();
  state.asistencia.anio = anio;
  const cursos = await api(`/cursos?activo=true&anio_academico=${anio}`);
  state.asistencia.cursos = cursos;
  const cursoSelect = qs("#asistencia-curso");
  const selectedCurso = cursoSelect?.value || cursos[0]?.id || "";

  if (cursoSelect) {
    cursoSelect.innerHTML = "";
    const emptyOption = document.createElement("option");
    emptyOption.value = "";
    emptyOption.textContent = "Seleccione curso";
    cursoSelect.appendChild(emptyOption);

    cursos.forEach((curso) => {
      const option = document.createElement("option");
      option.value = String(curso.id);
      option.textContent = curso.nombre;
      cursoSelect.appendChild(option);
    });

    cursoSelect.value = selectedCurso ? String(selectedCurso) : "";
  }
  if (!cursos.length) {
    showMessage("#asistencia-message", "No hay cursos activos para el año seleccionado. Crea o activa un curso desde Calendario.", true);
  } else {
    clearMessage("#asistencia-message");
  }
}

async function loadAsistenciaResumen() {
  const cursoId = asistenciaCursoId();
  const fecha = new Date(`${asistenciaFecha()}T00:00:00`);
  const mes = fecha.getMonth() + 1;
  const params = new URLSearchParams();
  params.set("mes", mes);
  params.set("anio_academico", asistenciaAnio());
  if (cursoId) params.set("curso_id", cursoId);
  const resumen = await api(`/asistencias/resumen?${params.toString()}`);
  setText("#asistencia-presentes", resumen.presentes || 0);
  setText("#asistencia-tardes", resumen.tardes || 0);
  setText("#asistencia-justificados", resumen.justificados || 0);
  setText("#asistencia-porcentaje", resumen.porcentaje_asistencia === null || resumen.porcentaje_asistencia === undefined ? "-" : `${resumen.porcentaje_asistencia}%`);
}

async function loadAsistenciaDia() {
  clearMessage("#asistencia-message");
  const cursoId = asistenciaCursoId();
  const table = qs("#asistencia-table");
  const empty = qs("#asistencia-empty");
  if (!table || !empty) return;
  if (!cursoId) {
    table.innerHTML = "";
    empty.textContent = "Selecciona un curso y una fecha para registrar asistencia.";
    empty.classList.remove("hidden");
    await loadAsistenciaResumen();
    return;
  }
  const anio = asistenciaAnio();
  const fecha = asistenciaFecha();
  const [estudiantes, registros] = await Promise.all([
    api(`/estudiantes?activo=true&curso_id=${cursoId}&anio_academico=${anio}`),
    api(`/asistencias?curso_id=${cursoId}&fecha=${fecha}&anio_academico=${anio}`),
  ]);
  state.asistencia.estudiantes = estudiantes;
  state.asistencia.registros = registros;
  const registroPorEstudiante = new Map(registros.map((registro) => [registro.estudiante_id, registro]));
  table.innerHTML = estudiantes
    .map((estudiante) => {
      const registro = registroPorEstudiante.get(estudiante.id);
      return `
        <tr data-estudiante-id="${estudiante.id}">
          <td>
            <strong>${escapeHtml(estudiante.nombre)} ${escapeHtml(estudiante.apellido)}</strong>
            <span class="muted-line">${escapeHtml(estudiante.rut || estudiante.correo || "Sin identificador")}</span>
          </td>
          <td>
            <select class="attendance-status">
              ${asistenciaStatusOptions(registro?.estado || "presente")}
            </select>
          </td>
          <td><input class="attendance-note" value="${escapeHtml(registro?.observacion || "")}" placeholder="Observacion opcional"></td>
        </tr>
      `;
    })
    .join("");
  empty.textContent = estudiantes.length ? "" : "Este curso no tiene estudiantes activos para el año seleccionado.";
  empty.classList.toggle("hidden", estudiantes.length > 0);
  await loadAsistenciaResumen();
}

async function saveAsistenciaDia() {
  const cursoId = asistenciaCursoId();
  if (!cursoId) throw new Error("Selecciona un curso antes de guardar asistencia.");
  const registros = qsa("#asistencia-table tr").map((row) => ({
    estudiante_id: Number(row.dataset.estudianteId),
    estado: row.querySelector(".attendance-status").value,
    observacion: row.querySelector(".attendance-note").value.trim() || null,
  }));
  if (!registros.length) throw new Error("No hay estudiantes para guardar asistencia.");
  await api("/asistencias/bulk", {
    method: "POST",
    body: JSON.stringify({
      curso_id: cursoId,
      fecha: asistenciaFecha(),
      anio_academico: asistenciaAnio(),
      registros,
    }),
  });
}

function bindAsistencia() {
  const fechaInput = qs("#asistencia-fecha");
  if (fechaInput && !fechaInput.value) fechaInput.value = new Date().toISOString().slice(0, 10);
  qs("#asistencia-cargar")?.addEventListener("click", loadAsistenciaDia);
  qs("#asistencia-curso")?.addEventListener("change", loadAsistenciaDia);
  qs("#asistencia-fecha")?.addEventListener("change", loadAsistenciaDia);
  qs("#asistencia-anio")?.addEventListener("change", async () => {
    await loadAsistenciaCatalogs();
    await loadAsistenciaDia();
  });
  qs("#asistencia-guardar")?.addEventListener("click", async () => {
    try {
      await saveAsistenciaDia();
      showMessage("#asistencia-message", "Asistencia guardada correctamente.");
      await loadAsistenciaDia();
    } catch (error) {
      showMessage("#asistencia-message", error.message, true);
    }
  });
}

async function initAsistencia() {
  bindAsistencia();
  await loadAsistenciaCatalogs();
  await loadAsistenciaDia();
}

document.addEventListener("DOMContentLoaded", async () => {
  const page = document.body.dataset.page;
  if (page !== "login" && !sessionStorage.getItem("kairos-user")) {
    window.location.href = "login.html";
    return;
  }

  bindShell();
  bindLogin();
  await checkApiStatus();
  try {
    if (page === "dashboard") await initDashboard();
    if (page === "cursos") {
      bindCursos();
      await loadCursos();
    }
    if (page === "estudiantes") await initEstudiantesAdmin();
    if (page === "perfil-estudiante") await initPerfilEstudiante();
    if (page === "profesores") {
      bindProfesores();
      await loadProfesores();
    }
    if (page === "asignaturas") {
      bindAsignaturas();
      await loadAsignaturas();
    }
    if (page === "asignaciones") {
      bindAsignaciones();
      await fillAsignacionSelects();
      await loadAsignaciones();
    }
    if (page === "calendario") await initCalendario();
    if (page === "notas") await initNotas();
    if (page === "asistencia") await initAsistencia();
  } catch (error) {
    console.error(error);
    const pageMessages = {
      cursos: ["#curso-message", "cursos"],
      estudiantes: ["#estudiante-admin-message", "estudiantes"],
      profesores: ["#profesor-message", "profesores"],
      asignaturas: ["#asignatura-message", "asignaturas"],
      asignaciones: ["#asignacion-message", "asignaciones"],
      calendario: ["#calendario-message", "calendario"],
      notas: ["#notas-message", "notas"],
      asistencia: ["#asistencia-message", "asistencia"],
      "perfil-estudiante": ["#perfil-message", "perfil"],
    };
    const pageMessage = pageMessages[page];
    if (pageMessage) {
      showMessage(pageMessage[0], `No se pudo cargar ${pageMessage[1]}: ${error.message}`, true);
    }
  }
});
