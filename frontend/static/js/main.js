const API_BASE_URL = "http://localhost:8000/api";
const HEALTH_URL = "http://localhost:8000/health";

const state = {
  profesores: [],
  asignaturas: [],
  asignaciones: [],
  calendario: {
    anio: 2026,
    mes: 6,
    cursos: [],
    items: [],
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

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = data.detail;
    const message = Array.isArray(detail)
      ? detail.map((item) => item.msg || item.detail || JSON.stringify(item)).join(" ")
      : detail || "No se pudo completar la solicitud.";
    throw new Error(message);
  }
  return data;
}

async function checkApiStatus() {
  const status = qs("#api-status");
  if (!status) return;
  try {
    await fetch(HEALTH_URL);
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
      const height = Math.max((item.total / max) * 170, item.total > 0 ? 18 : 8);
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
    setText("#total-asignaciones", resumen.total_asignaciones);
    setText("#total-mes", resumen.asignaciones_mes_destacado);
    setText("#mes-activo", resumen.mes_mas_activo);
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
  } catch {
    setText("#total-profesores", "0");
    setText("#total-asignaturas", "0");
    setText("#total-asignaciones", "0");
    setText("#total-mes", "0");
    setText("#mes-activo", "Sin datos");
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
            <button class="button button-blue action-button" data-edit-profesor="${profesor.id}" title="Editar">Edit</button>
            <button class="button ${profesor.activo ? "button-light" : "button-green"} action-button" data-toggle-profesor="${profesor.id}" title="${profesor.activo ? "Desactivar" : "Activar"}">${profesor.activo ? "Des" : "Act"}</button>
            <button class="button button-red action-button" data-delete-profesor="${profesor.id}" title="Eliminar">Del</button>
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
            <button class="button button-blue action-button" data-edit-asignatura="${asignatura.id}" title="Editar">Edit</button>
            <button class="button ${asignatura.activo ? "button-light" : "button-green"} action-button" data-toggle-asignatura="${asignatura.id}" title="${asignatura.activo ? "Desactivar" : "Activar"}">${asignatura.activo ? "Des" : "Act"}</button>
            <button class="button button-red action-button" data-delete-asignatura="${asignatura.id}" title="Eliminar">Del</button>
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
            <button class="button button-red action-button" data-delete-asignacion="${asignacion.id}" title="Eliminar">Del</button>
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
  evaluacion: "Evaluacion",
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
  select.innerHTML =
    option(firstLabel, "", String(selectedValue) === "") +
    items.map((item) => option(labelBuilder(item), item.id, String(item.id) === String(selectedValue))).join("");
}

function setCalendarInputsDate() {
  const anio = state.calendario.anio;
  qs("#curso-anio") && (qs("#curso-anio").value = anio);
  qs("#horario-anio") && (qs("#horario-anio").value = anio);
}

function updateCalendarTitle() {
  setText("#calendar-title", `${MONTH_NAMES[state.calendario.mes - 1]} ${state.calendario.anio}`);
  setText("#calendar-subtitle", `Anio academico ${state.calendario.anio}`);
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
              <button class="button button-red action-button" type="button" ${deleteAttr}>Del</button>
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
  } catch (error) {
    console.error(error);
    if (page === "calendario") {
      showMessage("#calendario-message", `No se pudo cargar el calendario: ${error.message}`, true);
    }
  }
});
