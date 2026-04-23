let nextStart = 0;
let hasMore = false;
let isLoading = false;

const filterForm = document.getElementById("logFilterForm");
const resetBtn = document.getElementById("resetFilters");

const dateSelect = document.getElementById("logDate");
const kindSelect = document.getElementById("logKind");
const roleSelect = document.getElementById("logRole");
const durationSelect = document.getElementById("logDuration");

const tableBody = document.getElementById("logsTableBody");
const loadMoreBtn = document.getElementById("loadMore");
const metaEl = document.getElementById("logMeta");
const countEl = document.getElementById("logCount");

function setMeta(text) {
  if (!text) {
    metaEl.style.display = "none";
    metaEl.textContent = "";
    return;
  }
  metaEl.textContent = text;
  metaEl.style.display = "block";
}

function setCount(text) {
  if (!text) {
    countEl.style.display = "none";
    countEl.textContent = "";
    return;
  }
  countEl.textContent = text;
  countEl.style.display = "block";
}

function clearTable() {
  tableBody.innerHTML = "";
}

function safeText(value) {
  if (value === null || value === undefined) return "";
  return String(value);
}

function formatTs(ts) {
  try {
    const d = new Date(ts);
    if (Number.isNaN(d.getTime())) return safeText(ts);
    return d.toLocaleString("ru-RU");
  } catch {
    return safeText(ts);
  }
}

function durationLabel(ms) {
  const value = Number(ms);
  if (Number.isNaN(value)) return "";
  return `${value} мс`;
}

function renderCodeCell(title, content) {
  const wrapper = document.createElement("div");
  const details = document.createElement("details");
  details.className = "log-details";

  const summary = document.createElement("summary");
  summary.textContent = title;
  details.appendChild(summary);

  const pre = document.createElement("pre");
  pre.className = "log-code";
  pre.textContent = content || "";
  details.appendChild(pre);

  wrapper.appendChild(details);
  return wrapper;
}

function renderStatusCell(entry) {
  const container = document.createElement("div");
  container.className = "log-status";

  const pill = document.createElement("span");
  pill.className = `log-pill ${entry.success ? "ok" : "err"}`;
  pill.textContent = entry.success ? "успешно" : "ошибка";
  container.appendChild(pill);

  if (!entry.success && entry.error) {
    const err = document.createElement("span");
    err.className = "log-error-text";
    err.textContent = safeText(entry.error);
    container.appendChild(err);
  }

  return container;
}

function renderRow(entry) {
  const tr = document.createElement("tr");

  const tdTs = document.createElement("td");
  tdTs.textContent = formatTs(entry.ts);
  tr.appendChild(tdTs);

  const tdIp = document.createElement("td");
  tdIp.textContent = safeText(entry.ip);
  tr.appendChild(tdIp);

  const tdAcc = document.createElement("td");
  tdAcc.textContent = safeText(entry.account_id);
  tr.appendChild(tdAcc);

  const tdRole = document.createElement("td");
  tdRole.textContent = safeText(entry.role);
  tr.appendChild(tdRole);

  const tdDur = document.createElement("td");
  tdDur.textContent = durationLabel(entry.duration_ms);
  tr.appendChild(tdDur);

  const tdSql = document.createElement("td");
  tdSql.appendChild(renderCodeCell(entry.kind ? `${entry.kind.toUpperCase()}` : "SQL", safeText(entry.sql)));
  tr.appendChild(tdSql);

  const tdParams = document.createElement("td");
  if (entry.params_hidden) {
    tdParams.appendChild(renderCodeCell("Скрыто", "Параметры скрыты"));
  } else {
    const paramsText =
      entry.params === null || entry.params === undefined
        ? ""
        : JSON.stringify(entry.params, null, 2);
    tdParams.appendChild(renderCodeCell("JSON", paramsText));
  }
  tr.appendChild(tdParams);

  const tdStatus = document.createElement("td");
  tdStatus.appendChild(renderStatusCell(entry));
  tr.appendChild(tdStatus);

  return tr;
}

function updateLoadMore() {
  loadMoreBtn.style.display = hasMore ? "inline-flex" : "none";
  loadMoreBtn.disabled = isLoading;
}

function buildQuery(start) {
  const params = new URLSearchParams();
  params.set("date", dateSelect.value);
  params.set("start", String(start || 0));
  params.set("limit", "200");

  if (kindSelect.value) params.set("kind", kindSelect.value);
  if (roleSelect.value) params.set("role", roleSelect.value);
  if (durationSelect.value) params.set("duration", durationSelect.value);

  return params.toString();
}

async function fetchDates() {
  const res = await fetch("/api/db_logs/dates");
  const data = await res.json();
  if (!data.success) throw new Error(data.error || "Не удалось получить список дат");
  return data.dates || [];
}

function fillDates(dates) {
  dateSelect.innerHTML = "";
  dates.forEach((d) => {
    const opt = document.createElement("option");
    opt.value = d;
    opt.textContent = d;
    dateSelect.appendChild(opt);
  });
}

async function loadLogs(reset = false) {
  if (isLoading) return;
  if (!dateSelect.value) return;

  isLoading = true;
  updateLoadMore();
  setMeta("");

  try {
    const start = reset ? 0 : nextStart;
    const query = buildQuery(start);

    const res = await fetch(`/api/db_logs?${query}`);
    const data = await res.json();

    if (!data.success) {
      throw new Error(data.error || "Ошибка при загрузке логов");
    }

    if (reset) clearTable();

    const items = data.items || [];
    items.forEach((entry) => tableBody.appendChild(renderRow(entry)));

    nextStart = data.next_start || 0;
    hasMore = Boolean(data.has_more);

    setCount(`Показано: ${tableBody.children.length}${hasMore ? " (есть ещё)" : ""}`);
  } catch (err) {
    setMeta(`Ошибка: ${err.message || String(err)}`);
  } finally {
    isLoading = false;
    updateLoadMore();
  }
}

function resetFilters() {
  kindSelect.value = "";
  roleSelect.value = "";
  durationSelect.value = "";
}

filterForm.addEventListener("submit", (e) => {
  e.preventDefault();
  loadLogs(true);
});

resetBtn.addEventListener("click", () => {
  resetFilters();
  loadLogs(true);
});

loadMoreBtn.addEventListener("click", () => {
  if (!hasMore) return;
  loadLogs(false);
});

async function init() {
  try {
    setMeta("Загрузка списка дат…");
    const dates = await fetchDates();
    if (!dates.length) {
      setMeta("Логи не найдены.");
      fillDates([]);
      clearTable();
      hasMore = false;
      updateLoadMore();
      setCount("");
      return;
    }

    fillDates(dates);
    dateSelect.value = dates[0];

    setMeta("");
    await loadLogs(true);
  } catch (err) {
    setMeta(`Ошибка: ${err.message || String(err)}`);
  }
}

init();

