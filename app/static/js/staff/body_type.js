// Глобальные переменные
let bodyTypes = [];
let editMode = false;
let currentEditId = null;

// DOM элементы
const bodyTypesTableBody = document.getElementById('bodyTypesTableBody');
const addForm = document.getElementById('add-form');
const bodyTypeNameInput = document.getElementById('bodyTypeName');
const errorMessage = document.getElementById('errorMessage');

// Показать ошибку
function showError(message) {
   errorMessage.textContent = message;
   errorMessage.style.display = 'block';

   // Автоматически скрыть через 10 секунд
   setTimeout(() => {
      errorMessage.style.display = 'none';
   }, 10000);
}

// Скрыть ошибку
function hideError() {
   errorMessage.style.display = 'none';
}

// Загрузить все бренды
async function loadBodyTypes() {
   try {
      const response = await fetch('/api/crud/body_types');
      const result = await response.json();

      if (result.success) {
         bodyTypes = result.data;
         renderBodyTypesTable();
      } else {
         showError('Ошибка при загрузке данных: ' + result.error);
      }
   } catch (error) {
      showError('Ошибка сети: ' + error.message);
   }
}

// Отобразить таблицы типов кузовов
function renderBodyTypesTable() {
   bodyTypesTableBody.innerHTML = '';

   bodyTypes.forEach(bodyType => {
      const row = document.createElement('tr');
      row.id = `body-type-row-${bodyType.id}`;
      row.innerHTML = `
            <td id="body-type-name-${bodyType.id}">${escapeHtml(bodyType.name)}</td>
            <td>
                <button class="btn-outline edit-btn" data-id="${bodyType.id}">Изменить</button>
            </td>
        `;
      bodyTypesTableBody.appendChild(row);
   });

   // Добавить обработчики для кнопок "Изменить"
   document.querySelectorAll('.edit-btn').forEach(button => {
      button.addEventListener('click', function () {
         const id = parseInt(this.getAttribute('data-id'));
         enterEditMode(id);
      });
   });
}

// Войти в режим редактирования
function enterEditMode(id) {
   if (editMode) {
      cancelEdit();
   }

   const bodyType = bodyTypes.find(b => b.id === id);
   if (!bodyType) return;

   currentEditId = id;
   editMode = true;

   const nameCell = document.getElementById(`body-type-name-${id}`);
   const actionCell = nameCell.nextElementSibling;

   // Сохраняем оригинальное значение
   const originalName = bodyType.name;

   // Создаем панель редактирования
   const editPanel = document.createElement('div');
   editPanel.className = 'edit-panel';
   editPanel.id = `edit-panel-${id}`;
   editPanel.innerHTML = `
        <input type="text" id="edit-input-${id}" value="${escapeHtml(originalName)}" class="edit-input">
        <div class="edit-buttons">
            <button class="btn-outline" id="btn-save-${id}" data-id="${id}">Сохранить</button>
            <button class="btn-outline" id="btn-cancel-${id}" data-id="${id}">Отмена</button>
            <button class="btn-red" id="btn-delete-${id}" data-id="${id}">Удалить</button>
        </div>
    `;

   // Скрываем оригинальный контент
   nameCell.style.display = 'none';

   // Вставляем панель редактирования
   nameCell.parentNode.insertBefore(editPanel, actionCell);

   // Фокусируемся на поле ввода
   const input = document.getElementById(`edit-input-${id}`);
   input.focus();
   input.select();

   // Добавляем обработчики для кнопок панели
   document.getElementById(`btn-save-${id}`).addEventListener('click', saveBodyType);
   document.getElementById(`btn-cancel-${id}`).addEventListener('click', cancelEdit);
   document.getElementById(`btn-delete-${id}`).addEventListener('click', deleteBrand);

   // Обработка нажатия Enter и Escape
   input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') {
         saveBodyType();
      } else if (e.key === 'Escape') {
         cancelEdit();
      }
   });
}

// Сохранить изменение названия кузова
async function saveBodyType() {
   if (!currentEditId) return;

   const input = document.getElementById(`edit-input-${currentEditId}`);
   const newName = input.value.trim();

   if (!newName) {
      showError('Название не может быть пустым');
      input.focus();
      return;
   }

   try {
      const response = await fetch(`/api/crud/body_types/${currentEditId}`, {
         method: 'PUT',
         headers: {
            'Content-Type': 'application/json',
         },
         body: JSON.stringify({ name: newName })
      });

      const result = await response.json();

      if (result.success) {
         // Обновляем локальные данные
         const brandIndex = bodyTypes.findIndex(b => b.id === currentEditId);
         if (brandIndex !== -1) {
            bodyTypes[brandIndex].name = newName;
         }

         // Выходим из режима редактирования
         exitEditMode();

         // Перерисовываем таблицу
         renderBodyTypesTable();

         hideError();
      } else {
         showError('Ошибка при сохранении: ' + result.error);
         input.focus();
         input.select();
      }
   } catch (error) {
      showError('Ошибка сети: ' + error.message);
   }
}

// Удалить тип кузова
async function deleteBrand() {
   if (!currentEditId) return;

   if (!confirm('Вы уверены, что хотите удалить этот тип кузова?')) {
      return;
   }

   try {
      const response = await fetch(`/api/crud/body_types/${currentEditId}`, {
         method: 'DELETE'
      });

      const result = await response.json();

      if (result.success) {
         // Удаляем из локальных данных
         bodyTypes = bodyTypes.filter(b => b.id !== currentEditId);

         // Выходим из режима редактирования
         exitEditMode();

         // Перерисовываем таблицу
         renderBodyTypesTable();

         hideError();
      } else {
         showError('Ошибка при удалении: ' + result.error);
      }
   } catch (error) {
      showError('Ошибка сети: ' + error.message);
   }
}

// Отменить редактирование
function cancelEdit() {
   exitEditMode();
   renderBodyTypesTable();
}

// Выйти из режима редактирования
function exitEditMode() {
   if (currentEditId && editMode) {
      const editPanel = document.getElementById(`edit-panel-${currentEditId}`);
      if (editPanel) {
         editPanel.remove();
      }

      const nameCell = document.getElementById(`body-type-name-${currentEditId}`);
      if (nameCell) {
         nameCell.style.display = '';
      }

      currentEditId = null;
      editMode = false;
   }
}

// Добавить новый тип кузова
addForm.addEventListener('submit', async function (e) {
   e.preventDefault();

   const name = bodyTypeNameInput.value.trim();

   if (!name) {
      showError('Введите тип кузова');
      return;
   }

   try {
      const response = await fetch('/api/crud/body_types', {
         method: 'POST',
         headers: {
            'Content-Type': 'application/json',
         },
         body: JSON.stringify({ name: name })
      });

      const result = await response.json();

      if (result.success) {
         // Добавляем новый тип кузова в локальные данные
         bodyTypes.push({
            id: result.id,
            name: name
         });

         // Перерисовываем таблицу
         renderBodyTypesTable();

         // Очищаем форму
         bodyTypeNameInput.value = '';
         hideError();
      } else {
         showError('Ошибка при добавлении: ' + result.error);
      }
   } catch (error) {
      showError('Ошибка сети: ' + error.message);
   }
});

// Экранирование HTML для безопасности
function escapeHtml(text) {
   const div = document.createElement('div');
   div.textContent = text;
   return div.innerHTML;
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function () {
   loadBodyTypes();
});