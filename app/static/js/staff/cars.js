let objects = [];
let editMode = false;
let currentEditId = null;

const objectTableBody = document.getElementById("objectsTableBody");
const addForm = document.getElementById("addObjectForm");
const errorMessage = document.getElementById("errorMessage");
const brandSelect = document.getElementById("brandSelect");
const modelSelect = document.getElementById("modelSelect");
const colorSelect = document.getElementById("colorSelect");
const vinInput = document.getElementById("vinInput");

const allModels = window.models || [];

function showError(message) {
  errorMessage.textContent = message;
  errorMessage.style.display = "block";
}

function hideError() {
  errorMessage.style.display = "none";
}

function fillModelSelect(selectEl, brandId, selectedModelId = null) {
  selectEl.innerHTML = '<option value="" disabled selected>Модель</option>';

  if (!brandId) {
    selectEl.disabled = true;
    return;
  }

  const filteredModels = allModels.filter((m) => m.brand_id === Number(brandId));
  filteredModels.forEach((model) => {
    const option = document.createElement("option");
    option.value = model.id;
    option.textContent = model.model;
    if (selectedModelId && model.id === Number(selectedModelId)) {
      option.selected = true;
    }
    selectEl.appendChild(option);
  });

  selectEl.disabled = filteredModels.length === 0;
}

async function loadObjects() {
  try {
    const response = await fetch("/api/crud/cars");
    const result = await response.json();

    if (result.success) {
      objects = result.data;
      renderObjectTable();
    } else {
      showError("Ошибка при загрузке данных: " + result.error);
    }
  } catch (error) {
    showError("Ошибка сети: " + error.message);
  }
}

function renderObjectTable() {
  objectTableBody.innerHTML = "";

  objects.forEach((car) => {
    const row = document.createElement("tr");
    row.id = `object-row-${car.id}`;
    row.innerHTML = `
      <td data-sort-key="brand">${car.brand}</td>
      <td data-sort-key="model">${car.model}</td>
      <td data-sort-key="vin">${car.vin}</td>
      <td data-sort-key="color">${car.color}</td>
      <td data-sort-key="status"><span class="status ${car.is_sold ? "sold" : "available"}">${car.is_sold ? "Куплен" : "В продаже"}</span></td>
      <td><button class="btn-outline edit-btn" data-id="${car.id}">Изменить</button></td>
    `;
    objectTableBody.appendChild(row);
  });

  document.querySelectorAll(".edit-btn").forEach((button) => {
    button.addEventListener("click", function () {
      enterEditMode(parseInt(this.getAttribute("data-id"), 10));
    });
  });
}

function enterEditMode(id) {
  if (editMode) cancelEdit();

  const car = objects.find((c) => c.id === id);
  if (!car) return;

  currentEditId = id;
  editMode = true;

  const row = document.getElementById(`object-row-${id}`);
  const editRow = document.createElement("tr");
  editRow.id = `edit-row-${id}`;
  editRow.classList.add("edit-panel");
  editRow.innerHTML = `
    <td colspan="6">
      <div class="edit-form-grid" style="display:grid;grid-template-columns:repeat(4,minmax(180px,1fr));gap:12px;">
        <select id="edit-brand-${id}" class="edit-input">
          <option value="" disabled>Производитель</option>
          ${(window.brands || [])
            .map(
              (brand) =>
                `<option value="${brand.id}" ${brand.id === car.brand_id ? "selected" : ""}>${brand.name}</option>`
            )
            .join("")}
        </select>
        <select id="edit-model-${id}" class="edit-input"></select>
        <select id="edit-color-${id}" class="edit-input">
          <option value="" disabled>Цвет</option>
          ${(window.colors || [])
            .map(
              (color) =>
                `<option value="${color.id}" ${color.id === car.color_id ? "selected" : ""}>${color.name}</option>`
            )
            .join("")}
        </select>
        <input type="text" id="edit-vin-${id}" class="edit-input" value="${car.vin}" minlength="17" maxlength="17">
      </div>
      <div class="edit-buttons" style="margin-top:12px;">
        <button class="btn-outline" id="btn-save-${id}">Сохранить</button>
        <button class="btn-outline" id="btn-cancel-${id}">Отмена</button>
        <button class="btn-red" id="btn-delete-${id}">Удалить</button>
      </div>
    </td>
  `;

  row.style.display = "none";
  row.parentNode.insertBefore(editRow, row.nextSibling);

  const editBrandSelect = document.getElementById(`edit-brand-${id}`);
  const editModelSelect = document.getElementById(`edit-model-${id}`);
  fillModelSelect(editModelSelect, car.brand_id, car.model_id);

  editBrandSelect.addEventListener("change", () => {
    fillModelSelect(editModelSelect, editBrandSelect.value);
  });

  document.getElementById(`btn-save-${id}`).addEventListener("click", saveObject);
  document.getElementById(`btn-cancel-${id}`).addEventListener("click", cancelEdit);
  document.getElementById(`btn-delete-${id}`).addEventListener("click", deleteObject);
}

async function saveObject() {
  if (!currentEditId) return;

  const brandId = document.getElementById(`edit-brand-${currentEditId}`).value;
  const modelId = document.getElementById(`edit-model-${currentEditId}`).value;
  const colorId = document.getElementById(`edit-color-${currentEditId}`).value;
  const vin = document.getElementById(`edit-vin-${currentEditId}`).value.trim().toUpperCase();

  if (!brandId || !modelId || !colorId || vin.length !== 17) {
    showError("Заполните все поля, VIN должен содержать 17 символов");
    return;
  }

  try {
    const response = await fetch(`/api/crud/cars/${currentEditId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model_id: Number(modelId), color_id: Number(colorId), vin }),
    });

    const result = await response.json();
    if (result.success) {
      hideError();
      exitEditMode();
      await loadObjects();
    } else {
      showError("Ошибка при сохранении: " + result.error);
    }
  } catch (error) {
    showError("Ошибка сети: " + error.message);
  }
}

async function deleteObject() {
  if (!currentEditId) return;
  if (!confirm("Вы уверены, что хотите удалить этот автомобиль?")) return;

  try {
    const response = await fetch(`/api/crud/cars/${currentEditId}`, { method: "DELETE" });
    const result = await response.json();

    if (result.success) {
      hideError();
      exitEditMode();
      await loadObjects();
    } else {
      showError("Ошибка при удалении: " + result.error);
    }
  } catch (error) {
    showError("Ошибка сети: " + error.message);
  }
}

function cancelEdit() {
  exitEditMode();
  renderObjectTable();
}

function exitEditMode() {
  if (currentEditId && editMode) {
    const editRow = document.getElementById(`edit-row-${currentEditId}`);
    if (editRow) editRow.remove();

    const row = document.getElementById(`object-row-${currentEditId}`);
    if (row) row.style.display = "";

    currentEditId = null;
    editMode = false;
  }
}

brandSelect.addEventListener("change", () => {
  fillModelSelect(modelSelect, brandSelect.value);
});

addForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const modelId = modelSelect.value;
  const colorId = colorSelect.value;
  const vin = vinInput.value.trim().toUpperCase();

  if (!brandSelect.value || !modelId || !colorId || vin.length !== 17) {
    showError("Заполните все поля, VIN должен содержать 17 символов");
    return;
  }

  try {
    const response = await fetch("/api/crud/cars", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model_id: Number(modelId), color_id: Number(colorId), vin }),
    });

    const result = await response.json();

    if (result.success) {
      addForm.reset();
      modelSelect.innerHTML = '<option value="" disabled selected>Модель</option>';
      modelSelect.disabled = true;
      hideError();
      await loadObjects();
    } else {
      showError("Ошибка при добавлении: " + result.error);
    }
  } catch (error) {
    showError("Ошибка сети: " + error.message);
  }
});

loadObjects();
