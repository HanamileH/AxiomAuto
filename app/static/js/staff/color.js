// Глобальные переменные
let objects = [];
let editMode = false;
let currentEditId = null;

// DOM элементы
const objectTableBody = document.getElementById("objectsTableBody");
const addForm = document.getElementById("addObjectForm");
const errorMessage = document.getElementById("errorMessage");

// Элементы ввода
const colorNameInput = document.getElementById("colorName");
const colorValueInput = document.getElementById("colorValue");

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
    const response = await fetch("/api/crud/colors");
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

  objects.forEach((color) => {
    const row = document.createElement("tr");
    row.id = `object-row-${color.id}`;
    row.innerHTML = `
         <td id="color-value-${color.id}">
            <div class="color-preview" id="color-preview-${color.id}" style="background-color: #${color.hex_code};"></div>
         </td>
         <td id="color-name-${color.id}">${color.name}</td>
         <td>
            <button class="btn-outline edit-btn" data-id="${color.id}">Изменить</button>
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

// Войти в режим редактирования
function enterEditMode(id) {
  if (editMode) {
    cancelEdit();
  }

  const object = objects.find((c) => c.id === id);
  if (!object) return;

  currentEditId = id;
  editMode = true;

  const row = document.getElementById(`object-row-${id}`);
  if (!row) return;

  // Сохраняем оригинальные значения
  const originalName = object.name;
  const originalValue = object.hex_code;

  // Создаем панель редактирования (отдельную строку таблицы)
  const editRow = document.createElement("tr");
  editRow.id = `edit-row-${id}`;
  editRow.classList.add("edit-panel");
  editRow.innerHTML = `
      <td>
         <input type="color" id="edit-color-value-${id}" value="#${originalValue}" class="color-input">
      </td>
      <td>
         <input type="text" id="edit-input-${id}" value="${originalName}" class="edit-input" placeholder="Название цвета">
      </td>
      <td>
      <div class="edit-buttons">
         <button class="btn-outline" id="btn-save-${id}" data-id="${id}">Сохранить</button>
         <button class="btn-outline" id="btn-cancel-${id}" data-id="${id}">Отмена</button>
         <button class="btn-red" id="btn-delete-${id}" data-id="${id}">Удалить</button>
      </div>
      </td>
   `;

  // Скрываем оригинальную строку и вставляем панель редактирования вместо нее
  row.style.display = "none";
  row.parentNode.insertBefore(editRow, row.nextSibling);

  // Фокусируемся на поле ввода названия
  const nameInput = document.getElementById(`edit-input-${id}`);
  nameInput.focus();
  nameInput.select();

  // Добавляем обработчик для изменения цвета (обновление превью)
  const colorInput = document.getElementById(`edit-color-value-${id}`);
  const colorPreview = document.querySelector(`#color-preview-${id}`);

  colorInput.addEventListener("input", function () {
    // Обновляем предпросмотр цвета, если он есть
    if (colorPreview) {
      colorPreview.style.backgroundColor = this.value;
    }
  });

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

  // Обработка нажатия Enter и Escape
  nameInput.addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
      saveObject();
    } else if (e.key === "Escape") {
      cancelEdit();
    }
  });
}

// Сохранить изменения объекта
async function saveObject() {
  if (!currentEditId) return;

  const nameInput = document.getElementById(`edit-input-${currentEditId}`);
  const colorInput = document.getElementById(
    `edit-color-value-${currentEditId}`
  );

  const newName = nameInput.value.trim();
  const newValue = colorInput.value.trim().slice(1); // Убираем #

  if (!newName) {
    showError("Название не может быть пустым");
    nameInput.focus();
    return;
  }

  if (!newValue) {
    showError("Некорректный цвет");
    colorInput.focus();
    return;
  }

  try {
    const response = await fetch(`/api/crud/colors/${currentEditId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        name: newName,
        hex_code: newValue,
      }),
    });

    const result = await response.json();

    if (result.success) {
      // Обновляем локальные данные
      const colorIndex = objects.findIndex((c) => c.id === currentEditId);
      if (colorIndex !== -1) {
        objects[colorIndex].name = newName;
        objects[colorIndex].hex_code = newValue;
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

  if (!confirm("Вы уверены, что хотите удалить этот цвет?")) {
    return;
  }

  try {
    const response = await fetch(`/api/crud/colors/${currentEditId}`, {
      method: "DELETE",
    });

    const result = await response.json();

    if (result.success) {
      // Удаляем из локальных данных
      objects = objects.filter((c) => c.id !== currentEditId);

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

  const name = colorNameInput.value.trim();
  const value = colorValueInput.value.trim().slice(1); // Убираем #

  if (!name) {
    showError("Введите название цвета");
    colorNameInput.focus();
    return;
  }

  if (!value) {
    showError("Некорректный цвет");
    colorValueInput.focus();
    return;
  }

  try {
    const response = await fetch("/api/crud/colors", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        name: name,
        hex_code: value,
      }),
    });

    const result = await response.json();

    if (result.success) {
      // Добавляем новый объект в локальные данные
      objects.push({
        id: result.id,
        name: name,
        hex_code: value,
      });

      // Перерисовываем таблицу
      renderObjectTable();

      // Очищаем форму
      colorNameInput.value = "";
      colorValueInput.value = "#FFFFFF";
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
});
