// Глобальные переменные
let objects = [];
let editMode = false;
let currentEditId = null;

// DOM элементы
const objectTableBody = document.getElementById("objectsTableBody");
const addForm = document.getElementById("addObjectForm");
const errorMessage = document.getElementById("errorMessage");

// Элементы ввода формы добавления
const brandSelect = document.getElementById("brand_id");
const modelNameInput = document.getElementById("model_name");
const bodyTypeSelect = document.getElementById("body_type_id");
const descriptionInput = document.getElementById("description");
const yearInput = document.getElementById("year");
const engineTypeSelect = document.getElementById("engine_type");
const engineVolumeInput = document.getElementById("engine_volume");
const enginePowerInput = document.getElementById("engine_power");
const transmissionSelect = document.getElementById("transmission");
const priceInput = document.getElementById("price");
const imageInput = document.getElementById("image");

// Показать ошибку
function showError(message) {
  errorMessage.textContent = message;
  errorMessage.style.display = "block";
}

// Скрыть ошибку
function hideError() {
  errorMessage.style.display = "none";
}

// Загрузить все объекты
async function loadObjects() {
  try {
    const response = await fetch("/api/crud/models");
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

// Отобразить таблицу объектов
function renderObjectTable() {
  objectTableBody.innerHTML = "";

  objects.forEach((model) => {
    const row = document.createElement("tr");
    row.id = `object-row-${model.id}`;
    row.innerHTML = `
            <td id="brand-${model.id}">${model.brand}</td>
            <td id="model-name-${model.id}">${model.model}</td>
            <td id="body-type-${model.id}">${model.body_type}</td>
            <td id="description-${model.id}">${model.description}</td>
            <td id="year-${model.id}">${model.year || ""}</td>
            <td id="engine-type-${model.id}">${getEngineTypeLabel(
      model.engine_type
    )}</td>
            <td id="engine-volume-${model.id}">${
      model.engine_volume || "-"
    }</td>
            <td id="engine-power-${model.id}">${model.engine_power}</td>
            <td id="transmission-${model.id}">${getTransmissionLabel(
      model.transmission
    )}</td>
            <td id="price-${model.id}">${formatPrice(model.price)}</td>
            <td id="avaiable-${model.id}">${model.available_cars}</td>
            <td id="sold-${model.id}">${model.sold_cars}</td>
            <td>
                <button class="btn-outline edit-btn" data-id="${
                  model.id
                }">Изменить</button>
            </td>
        `;
    objectTableBody.appendChild(row);
  });

  // Добавить обработчики для кнопок "Изменить"
  document.querySelectorAll(".edit-btn").forEach((button) => {
    button.addEventListener("click", function () {
      const id = parseInt(this.getAttribute("data-id"));
      enterEditMode(id);
    });
  });
}

// Получить читаемое название типа двигателя
function getEngineTypeLabel(type) {
  const labels = {
    petrol: "Бензин",
    diesel: "Дизель",
    hybrid: "Гибрид",
    electric: "Электро",
  };
  return labels[type] || type;
}

// Получить читаемое название трансмиссии
function getTransmissionLabel(transmission) {
  const labels = {
    manual: "Механическая",
    automatic: "Автоматическая",
    variator: "Вариатор",
    robotic: "Роботизированная",
  };
  return labels[transmission] || transmission;
}

// Форматировать цену
function formatPrice(price) {
  return new Intl.NumberFormat("ru-RU").format(price);
}

// Войти в режим редактирования
function enterEditMode(id) {
  if (editMode) {
    cancelEdit();
  }

  const object = objects.find((m) => m.id === id);
  if (!object) return;

  currentEditId = id;
  editMode = true;

  const row = document.getElementById(`object-row-${id}`);
  if (!row) return;

  // Создаем панель редактирования (отдельную строку таблицы)
  const editRow = document.createElement("tr");
  editRow.id = `edit-row-${id}`;
  editRow.innerHTML = `
        <td colspan="11" style="padding: 0;">
            <div class="edit-panel" id="edit-panel-${id}">
                <div class="edit-form-grid">
                    <div class="form-group">
                        <label for="edit-brand-${id}">Производитель</label>
                        <select id="edit-brand-${id}" class="edit-input">
                            <option value="" disabled>Выберите производителя</option>
                            ${
                              window.brands
                                ? window.brands
                                    .map(
                                      (brand) =>
                                        `<option value="${brand.id}" ${
                                          brand.id === object.brand_id
                                            ? "selected"
                                            : ""
                                        }>${brand.name}</option>`
                                    )
                                    .join("")
                                : `<option value="${object.brand_id}" selected>${object.brand}</option>`
                            }
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="edit-name-${id}">Название модели</label>
                        <input type="text" id="edit-name-${id}" value="${
    object.model
  }" class="edit-input" placeholder="Название модели">
                    </div>
                    
                    <div class="form-group">
                        <label for="edit-body-type-${id}">Тип кузова</label>
                        <select id="edit-body-type-${id}" class="edit-input">
                            <option value="" disabled>Выберите тип кузова</option>
                            ${
                              window.bodyTypes
                                ? window.bodyTypes
                                    .map(
                                      (type) =>
                                        `<option value="${type.id}" ${
                                          type.id === object.body_type_id
                                            ? "selected"
                                            : ""
                                        }>${type.name}</option>`
                                    )
                                    .join("")
                                : `<option value="${object.body_type_id}" selected>${object.body_type}</option>`
                            }
                        </select>
                    </div>
                    
                    <div class="form-group span-2">
                        <label for="edit-description-${id}">Описание</label>
                        <textarea id="edit-description-${id}" class="edit-textarea" placeholder="Описание">${
    object.description
  }</textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="edit-year-${id}">Год</label>
                        <input type="number" id="edit-year-${id}" value="${
    object.year || ""
  }" class="edit-input" placeholder="Год" min="1900" max="2100">
                    </div>
                    
                    <div class="form-group">
                        <label for="edit-engine-type-${id}">Тип двигателя</label>
                        <select id="edit-engine-type-${id}" class="edit-input">
                            <option value="" disabled>Тип двигателя</option>
                            <option value="petrol" ${
                              object.engine_type === "petrol" ? "selected" : ""
                            }>Бензин</option>
                            <option value="diesel" ${
                              object.engine_type === "diesel" ? "selected" : ""
                            }>Дизель</option>
                            <option value="hybrid" ${
                              object.engine_type === "hybrid" ? "selected" : ""
                            }>Гибрид</option>
                            <option value="electric" ${
                              object.engine_type === "electric"
                                ? "selected"
                                : ""
                            }>Электро</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="edit-engine-volume-${id}">Объём двигателя (л.)</label>
                        <input type="number" id="edit-engine-volume-${id}" value="${
    object.engine_volume || ""
  }" class="edit-input" placeholder="Объём двигателя" step="0.1" min="0">
                    </div>
                    
                    <div class="form-group">
                        <label for="edit-engine-power-${id}">Мощность (л.с.)</label>
                        <input type="number" id="edit-engine-power-${id}" value="${
    object.engine_power
  }" class="edit-input" placeholder="Мощность" min="1">
                    </div>
                    
                    <div class="form-group">
                        <label for="edit-transmission-${id}">Трансмиссия</label>
                        <select id="edit-transmission-${id}" class="edit-input">
                            <option value="" disabled>Трансмиссия</option>
                            <option value="manual" ${
                              object.transmission === "manual" ? "selected" : ""
                            }>Механическая</option>
                            <option value="automatic" ${
                              object.transmission === "automatic"
                                ? "selected"
                                : ""
                            }>Автоматическая</option>
                            <option value="variator" ${
                              object.transmission === "variator"
                                ? "selected"
                                : ""
                            }>Вариатор</option>
                            <option value="robotic" ${
                              object.transmission === "robotic"
                                ? "selected"
                                : ""
                            }>Роботизированная</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="edit-price-${id}">Цена</label>
                        <input type="number" id="edit-price-${id}" value="${
    object.price
  }" class="edit-input" placeholder="Цена" min="1">
                    </div>

                    <div class="form-group">
                        <label for="edit-image-${id}">Фотография</label>
                        <input type="file" id="edit-image-${id}" class="edit-input" accept="image/png,image/jpeg,image/webp">
                    </div>
                </div>
                
                <div class="edit-buttons">
                    <button class="btn-outline" id="btn-save-${id}" data-id="${id}">Сохранить</button>
                    <button class="btn-outline" id="btn-cancel-${id}" data-id="${id}">Отмена</button>
                    <button class="btn-red" id="btn-delete-${id}" data-id="${id}">Удалить</button>
                </div>
            </div>
        </td>
    `;

  // Скрываем оригинальную строку и вставляем панель редактирования вместо нее
  row.style.display = "none";
  row.parentNode.insertBefore(editRow, row.nextSibling);

  // Фокусируемся на поле ввода названия
  const nameInput = document.getElementById(`edit-name-${id}`);
  nameInput.focus();
  nameInput.select();

  // Добавляем обработчики для кнопок панели
  document
    .getElementById(`btn-save-${id}`)
    .addEventListener("click", saveObject);
  document
    .getElementById(`btn-cancel-${id}`)
    .addEventListener("click", cancelEdit);
  document
    .getElementById(`btn-delete-${id}`)
    .addEventListener("click", deleteObject);

  // Обработка изменения типа двигателя
  const engineTypeSelect = document.getElementById(`edit-engine-type-${id}`);
  const engineVolumeInput = document.getElementById(`edit-engine-volume-${id}`);

  engineTypeSelect.addEventListener("change", function () {
    if (this.value === "electric") {
      engineVolumeInput.disabled = true;
      engineVolumeInput.value = "";
    } else {
      engineVolumeInput.disabled = false;
    }
  });

  // Инициализируем состояние объема двигателя
  if (engineTypeSelect.value === "electric") {
    engineVolumeInput.disabled = true;
  }

  // Обработка нажатия Enter в полях ввода
  nameInput.addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
      e.preventDefault();
      saveObject();
    }
  });
}

// Валидация данных модели
function validateModelData(data) {
  const errors = [];

  if (!data.brand_id) {
    errors.push("Выберите производителя");
  }

  if (!data.name || data.name.trim().length < 2) {
    errors.push("Название модели должно содержать минимум 2 символа");
  }

  if (!data.body_type_id) {
    errors.push("Выберите тип кузова");
  }

  if (!data.description || data.description.trim().length < 10) {
    errors.push("Описание должно содержать минимум 10 символов");
  }

  if (
    !data.year ||
    data.year < 1900 ||
    data.year > new Date().getFullYear() + 1
  ) {
    errors.push("Укажите корректный год");
  }

  if (!data.engine_type) {
    errors.push("Выберите тип двигателя");
  }

  if (
    data.engine_type !== "electric" &&
    (!data.engine_volume || data.engine_volume <= 0)
  ) {
    errors.push("Укажите объем двигателя");
  }

  if (!data.engine_power || data.engine_power <= 0) {
    errors.push("Укажите мощность двигателя");
  }

  if (!data.transmission) {
    errors.push("Выберите трансмиссию");
  }

  if (!data.price || data.price <= 0) {
    errors.push("Укажите корректную цену");
  }

  return errors;
}

// Сохранить изменения объекта
async function saveObject() {
  if (!currentEditId) return;

  const brandSelect = document.getElementById(`edit-brand-${currentEditId}`);
  const nameInput = document.getElementById(`edit-name-${currentEditId}`);
  const bodyTypeSelect = document.getElementById(`edit-body-type-${currentEditId}`);
  const descriptionInput = document.getElementById(`edit-description-${currentEditId}`);
  const yearInput = document.getElementById(`edit-year-${currentEditId}`);
  const engineTypeSelect = document.getElementById(`edit-engine-type-${currentEditId}`);
  const engineVolumeInput = document.getElementById(`edit-engine-volume-${currentEditId}`);
  const enginePowerInput = document.getElementById(`edit-engine-power-${currentEditId}`);
  const transmissionSelect = document.getElementById(`edit-transmission-${currentEditId}`);
  const priceInput = document.getElementById(`edit-price-${currentEditId}`);
  const imageInput = document.getElementById(`edit-image-${currentEditId}`);

  const data = {
    brand_id: parseInt(brandSelect.value),
    name: nameInput.value.trim(),
    body_type_id: parseInt(bodyTypeSelect.value),
    description: descriptionInput.value.trim(),
    year: parseInt(yearInput.value),
    engine_type: engineTypeSelect.value,
    engine_volume:
      engineTypeSelect.value !== "electric"
        ? parseFloat(engineVolumeInput.value)
        : null,
    engine_power: parseInt(enginePowerInput.value),
    transmission: transmissionSelect.value,
    price: parseFloat(priceInput.value),
  };

  // Валидация
  const errors = validateModelData(data);
  if (errors.length > 0) {
    showError(errors.join(", "));
    nameInput.focus();
    return;
  }

  try {
    const formData = new FormData();
    Object.entries(data).forEach(([key, value]) => {
      if (value !== null && value !== undefined && !Number.isNaN(value)) {
        formData.append(key, value);
      }
    });
    if (imageInput.files.length > 0) {
      formData.append("image", imageInput.files[0]);
    }

    const response = await fetch(`/api/crud/models/${currentEditId}`, {
      method: "PUT",
      body: formData,
    });

    const result = await response.json();

    if (result.success) {
      // Обновляем локальные данные
      const modelIndex = objects.findIndex((m) => m.id === currentEditId);
      if (modelIndex !== -1) {
        // Обновляем объект
        objects[modelIndex] = {
          ...objects[modelIndex],
          ...data,
        };
      }

      // Выходим из режима редактирования
      exitEditMode();

      // Перерисовываем таблицу
      renderObjectTable();

      hideError();
    } else {
      showError("Ошибка при сохранении: " + result.error);
      nameInput.focus();
      nameInput.select();
    }
  } catch (error) {
    showError("Ошибка сети: " + error.message);
  }
}

// Удалить объект
async function deleteObject() {
  if (!currentEditId) return;

  if (!confirm("Вы уверены, что хотите удалить эту модель?")) {
    return;
  }

  try {
    const response = await fetch(`/api/crud/models/${currentEditId}`, {
      method: "DELETE",
    });

    const result = await response.json();

    if (result.success) {
      // Удаляем из локальных данных
      objects = objects.filter((m) => m.id !== currentEditId);

      // Выходим из режима редактирования
      exitEditMode();

      // Перерисовываем таблицу
      renderObjectTable();

      hideError();
    } else {
      showError("Ошибка при удалении: " + result.error);
    }
  } catch (error) {
    showError("Ошибка сети: " + error.message);
  }
}

// Отменить редактирование
function cancelEdit() {
  exitEditMode();
  renderObjectTable();
}

// Выйти из режима редактирования
function exitEditMode() {
  if (currentEditId && editMode) {
    const editRow = document.getElementById(`edit-row-${currentEditId}`);
    if (editRow) {
      editRow.remove();
    }

    const row = document.getElementById(`object-row-${currentEditId}`);
    if (row) {
      row.style.display = "";
    }

    currentEditId = null;
    editMode = false;
  }
}

// Добавить новый объект
addForm.addEventListener("submit", async function (e) {
  e.preventDefault();

  const data = {
    brand_id: parseInt(brandSelect.value),
    name: modelNameInput.value.trim(),
    body_type_id: parseInt(bodyTypeSelect.value),
    description: descriptionInput.value.trim(),
    year: parseInt(yearInput.value),
    engine_type: engineTypeSelect.value,
    engine_volume:
      engineTypeSelect.value !== "electric"
        ? parseFloat(engineVolumeInput.value)
        : null,
    engine_power: parseInt(enginePowerInput.value),
    transmission: transmissionSelect.value,
    price: parseFloat(priceInput.value),
  };

  // Валидация
  const errors = validateModelData(data);
  if (errors.length > 0) {
    showError(errors.join(", "));
    modelNameInput.focus();
    return;
  }

  try {
    if (!imageInput.files.length) {
      showError("Добавьте фотографию модели");
      return;
    }

    const formData = new FormData();
    Object.entries(data).forEach(([key, value]) => {
      if (value !== null && value !== undefined && !Number.isNaN(value)) {
        formData.append(key, value);
      }
    });
    formData.append("image", imageInput.files[0]);

    const response = await fetch("/api/crud/models", {
      method: "POST",
      body: formData,
    });

    const result = await response.json();

    if (result.success) {
      // Добавляем новый объект в локальные данные
      objects.push({
        id: result.id,
        ...data,
        brand: window.brands
          ? window.brands.find((b) => b.id === data.brand_id)?.name || ""
          : "",
        body_type: window.bodyTypes
          ? window.bodyTypes.find((t) => t.id === data.body_type_id)?.name || ""
          : "",
      });

      // Перерисовываем таблицу
      renderObjectTable();

      // Очищаем форму
      addForm.reset();
      hideError();
    } else {
      showError("Ошибка при добавлении: " + result.error);
    }
  } catch (error) {
    showError("Ошибка сети: " + error.message);
  }
});

// Инициализация при загрузке страницы
document.addEventListener("DOMContentLoaded", function () {
  loadObjects();

  // Добавляем обработчик изменения типа двигателя в форме добавления
  engineTypeSelect.addEventListener("change", function () {
    if (this.value === "electric") {
      engineVolumeInput.disabled = true;
      engineVolumeInput.value = "";
    } else {
      engineVolumeInput.disabled = false;
    }
  });
});
