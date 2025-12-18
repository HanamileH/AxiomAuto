// Глобальные переменные
let objects = [];
let editMode = false;
let currentEditId = null;

// DOM элементы
const objectTableBody = document.getElementById('objectsTableBody');
const addForm = document.getElementById('add-form');
const errorMessage = document.getElementById('errorMessage');

// Элементы ввода
const objectNameInput = document.getElementById('brandName');

// Показать ошибку
function showError(message) {
   errorMessage.textContent = message;
   errorMessage.style.display = 'block';
}

// Скрыть ошибку
function hideError() {
   errorMessage.style.display = 'none';
}

// Загрузить все объекты
async function loadObjects() {
   try {
      const response = await fetch('/api/crud/brands');
      const result = await response.json();

      if (result.success) {
         objects = result.data;
         renderObjectTable();
      } else {
         showError('Ошибка при загрузке данных: ' + result.error);
      }
   } catch (error) {
      showError('Ошибка сети: ' + error.message);
   }
}

// Отобразить таблицу объектов
function renderObjectTable() {
   objectTableBody.innerHTML = '';

   objects.forEach(brand => {
      const row = document.createElement('tr');
      row.id = `object-row-${brand.id}`;
      row.innerHTML = `
            <td id="brand-name-${brand.id}">${brand.name}</td>
            <td>
                <button class="btn-outline edit-btn" data-id="${brand.id}">Изменить</button>
            </td>
        `;
      objectTableBody.appendChild(row);
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

   const object = objects.find(b => b.id === id);
   if (!object) return;

   currentEditId = id;
   editMode = true;

   const nameCell = document.getElementById(`brand-name-${id}`);
   const actionCell = nameCell.nextElementSibling;

   // Сохраняем оригинальное значение
   const originalName = object.name;

   // Создаем панель редактирования
   const editPanel = document.createElement('div');
   editPanel.className = 'edit-panel';
   editPanel.id = `edit-panel-${id}`;
   editPanel.innerHTML = `
        <input type="text" id="edit-input-${id}" value="${originalName}" class="edit-input">
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
   document.getElementById(`btn-save-${id}`).addEventListener('click', saveObject);
   document.getElementById(`btn-cancel-${id}`).addEventListener('click', cancelEdit);
   document.getElementById(`btn-delete-${id}`).addEventListener('click', deleteObject);

   // Обработка нажатия Enter и Escape
   input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') {
         saveObject();
      } else if (e.key === 'Escape') {
         cancelEdit();
      }
   });
}

// Сохранить изменения объекта
async function saveObject() {
   if (!currentEditId) return;

   const input = document.getElementById(`edit-input-${currentEditId}`);
   const newName = input.value.trim();

   if (!newName) {
      showError('Название не может быть пустым');
      input.focus();
      return;
   }

   try {
      const response = await fetch(`/api/crud/brands/${currentEditId}`, {
         method: 'PUT',
         headers: {
            'Content-Type': 'application/json',
         },
         body: JSON.stringify({ name: newName })
      });

      const result = await response.json();

      if (result.success) {
         // Обновляем локальные данные
         const brandIndex = objects.findIndex(b => b.id === currentEditId);
         if (brandIndex !== -1) {
            objects[brandIndex].name = newName;
         }

         // Выходим из режима редактирования
         exitEditMode();

         // Перерисовываем таблицу
         renderObjectTable();

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

// Удалить объект
async function deleteObject() {
   if (!currentEditId) return;

   if (!confirm('Вы уверены, что хотите удалить этот объект?')) {
      return;
   }

   try {
      const response = await fetch(`/api/crud/brands/${currentEditId}`, {
         method: 'DELETE'
      });

      const result = await response.json();

      if (result.success) {
         // Удаляем из локальных данных
         objects = objects.filter(b => b.id !== currentEditId);

         // Выходим из режима редактирования
         exitEditMode();

         // Перерисовываем таблицу
         renderObjectTable();

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
   renderObjectTable();
}

// Выйти из режима редактирования
function exitEditMode() {
   if (currentEditId && editMode) {
      const editPanel = document.getElementById(`edit-panel-${currentEditId}`);
      if (editPanel) {
         editPanel.remove();
      }

      const nameCell = document.getElementById(`brand-name-${currentEditId}`);
      if (nameCell) {
         nameCell.style.display = '';
      }

      currentEditId = null;
      editMode = false;
   }
}

// Добавить новый объект
addForm.addEventListener('submit', async function (e) {
   e.preventDefault();

   const name = objectNameInput.value.trim();

   if (!name) {
      showError('Введите название производителя');
      return;
   }

   try {
      const response = await fetch('/api/crud/brands', {
         method: 'POST',
         headers: {
            'Content-Type': 'application/json',
         },
         body: JSON.stringify({ name: name })
      });

      const result = await response.json();

      if (result.success) {
         // Добавляем новый объект в локальные данные
         objects.push({
            id: result.id,
            name: name
         });

         // Перерисовываем таблицу
         renderObjectTable();

         // Очищаем форму
         objectNameInput.value = '';
         hideError();
      } else {
         showError('Ошибка при добавлении: ' + result.error);
      }
   } catch (error) {
      showError('Ошибка сети: ' + error.message);
   }
});

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function () {
   loadObjects();
});