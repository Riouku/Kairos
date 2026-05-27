const API_BASE_URL = "http://localhost:8000/api";
const HEALTH_URL = "http://localhost:8000/health";

const state = {
  profesores: [],
  asignaturas: [],
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
    throw new Error(data.detail || "No se pudo completar la solicitud.");
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
          <span>${item.mes}</span>
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

async function loadProfesores(search = "") {
  const query = search ? `?search=${encodeURIComponent(search)}` : "";
  const profesores = await api(`/profesores${query}`);
  const table = qs("#profesores-table");
  table.innerHTML = profesores
    .map(
      (profesor) => `
        <tr>
          <td>${profesor.id}</td>
          <td>${profesor.nombre}</td>
          <td>${profesor.apellido}</td>
          <td>${profesor.correo}</td>
          <td class="actions">
            <button class="button button-blue action-button" data-edit-profesor="${profesor.id}" title="Editar">Edit</button>
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
  setText("#profesor-form-title", "Nuevo Profesor");
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
      correo: qs("#profesor-correo").value.trim(),
      telefono: qs("#profesor-telefono").value.trim() || null,
    };
    try {
      await api(id ? `/profesores/${id}` : "/profesores", {
        method: id ? "PUT" : "POST",
        body: JSON.stringify(payload),
      });
      showMessage("#profesor-message", id ? "Profesor actualizado correctamente." : "Profesor registrado correctamente.");
      resetProfesorForm();
      closeModal(qs("#profesor-modal"));
      await loadProfesores(qs("#profesor-search").value.trim());
    } catch (error) {
      showMessage("#profesor-message", error.message, true);
      window.alert(error.message);
    }
  });

  qs("#profesor-search").addEventListener("input", debounce((event) => loadProfesores(event.target.value.trim())));

  qs("#profesores-table").addEventListener("click", async (event) => {
    const editId = event.target.dataset.editProfesor;
    const deleteId = event.target.dataset.deleteProfesor;
    if (editId) {
      const profesor = state.profesores.find((item) => item.id === Number(editId));
      qs("#profesor-id").value = profesor.id;
      qs("#profesor-nombre").value = profesor.nombre;
      qs("#profesor-apellido").value = profesor.apellido;
      qs("#profesor-correo").value = profesor.correo;
      qs("#profesor-telefono").value = profesor.telefono || "";
      setText("#profesor-form-title", "Editar Profesor");
      openModal("#profesor-modal");
    }
    if (deleteId && window.confirm("Deseas eliminar este profesor?")) {
      try {
        await api(`/profesores/${deleteId}`, { method: "DELETE" });
        showMessage("#profesor-message", "Profesor eliminado correctamente.");
        await loadProfesores(qs("#profesor-search").value.trim());
      } catch (error) {
        showMessage("#profesor-message", error.message, true);
      }
    }
  });
}

async function loadAsignaturas(search = "") {
  const query = search ? `?search=${encodeURIComponent(search)}` : "";
  const asignaturas = await api(`/asignaturas${query}`);
  const table = qs("#asignaturas-table");
  table.innerHTML = asignaturas
    .map(
      (asignatura) => `
        <tr>
          <td>${asignatura.id}</td>
          <td>${asignatura.nombre}</td>
          <td>${asignatura.codigo}</td>
          <td>${asignatura.descripcion || "-"}</td>
          <td class="actions">
            <button class="button button-blue action-button" data-edit-asignatura="${asignatura.id}" title="Editar">Edit</button>
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
  setText("#asignatura-form-title", "Nueva Asignatura");
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
      await loadAsignaturas(qs("#asignatura-search").value.trim());
    } catch (error) {
      showMessage("#asignatura-message", error.message, true);
      window.alert(error.message);
    }
  });

  qs("#asignatura-search").addEventListener("input", debounce((event) => loadAsignaturas(event.target.value.trim())));

  qs("#asignaturas-table").addEventListener("click", async (event) => {
    const editId = event.target.dataset.editAsignatura;
    const deleteId = event.target.dataset.deleteAsignatura;
    if (editId) {
      const asignatura = state.asignaturas.find((item) => item.id === Number(editId));
      qs("#asignatura-id").value = asignatura.id;
      qs("#asignatura-nombre").value = asignatura.nombre;
      qs("#asignatura-codigo").value = asignatura.codigo;
      qs("#asignatura-descripcion").value = asignatura.descripcion || "";
      setText("#asignatura-form-title", "Editar Asignatura");
      openModal("#asignatura-modal");
    }
    if (deleteId && window.confirm("Deseas eliminar esta asignatura?")) {
      try {
        await api(`/asignaturas/${deleteId}`, { method: "DELETE" });
        showMessage("#asignatura-message", "Asignatura eliminada correctamente.");
        await loadAsignaturas(qs("#asignatura-search").value.trim());
      } catch (error) {
        showMessage("#asignatura-message", error.message, true);
      }
    }
  });
}

async function fillAsignacionSelects() {
  const [profesores, asignaturas] = await Promise.all([api("/profesores"), api("/asignaturas")]);
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
}

function bindAsignaciones() {
  qs("#ver-todas-asignaciones")?.addEventListener("click", () => loadAsignaciones());

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
  } catch (error) {
    console.error(error);
  }
});
