// Глобальные переменные
let brands = [];
let editMode = false;
let currentEditId = null;

// DOM элементы
const brandsTableBody = document.getElementById('brandsTableBody');
const addForm = document.getElementById('add-form');
const brandNameInput = document.getElementById('brandName');
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
async function loadBrands() {
   try {
      const response = await fetch('/api/crud/brands');
      const result = await response.json();

      if (result.success) {
         brands = result.data;
         renderBrandsTable();
      } else {
         showError('Ошибка при загрузке данных: ' + result.error);
      }
   } catch (error) {
      showError('Ошибка сети: ' + error.message);
   }
}

// Отобразить таблицу брендов
function renderBrandsTable() {
   brandsTableBody.innerHTML = '';

   brands.forEach(brand => {
      const row = document.createElement('tr');
      row.id = `brand-row-${brand.id}`;
      row.innerHTML = `
            <td id="brand-name-${brand.id}">${escapeHtml(brand.name)}</td>
            <td>
                <button class="btn-outline edit-btn" data-id="${brand.id}">Изменить</button>
            </td>
        `;
      brandsTableBody.appendChild(row);
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

   const brand = brands.find(b => b.id === id);
   if (!brand) return;

   currentEditId = id;
   editMode = true;

   const nameCell = document.getElementById(`brand-name-${id}`);
   const actionCell = nameCell.nextElementSibling;

   // Сохраняем оригинальное значение
   const originalName = brand.name;

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
   document.getElementById(`btn-save-${id}`).addEventListener('click', saveBrand);
   document.getElementById(`btn-cancel-${id}`).addEventListener('click', cancelEdit);
   document.getElementById(`btn-delete-${id}`).addEventListener('click', deleteBrand);

   // Обработка нажатия Enter и Escape
   input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') {
         saveBrand();
      } else if (e.key === 'Escape') {
         cancelEdit();
      }
   });
}

// Сохранить изменения бренда
async function saveBrand() {
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
         const brandIndex = brands.findIndex(b => b.id === currentEditId);
         if (brandIndex !== -1) {
            brands[brandIndex].name = newName;
         }

         // Выходим из режима редактирования
         exitEditMode();

         // Перерисовываем таблицу
         renderBrandsTable();

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

// Удалить бренд
async function deleteBrand() {
   if (!currentEditId) return;

   if (!confirm('Вы уверены, что хотите удалить этого производителя?')) {
      return;
   }

   try {
      const response = await fetch(`/api/crud/brands/${currentEditId}`, {
         method: 'DELETE'
      });

      const result = await response.json();

      if (result.success) {
         // Удаляем из локальных данных
         brands = brands.filter(b => b.id !== currentEditId);

         // Выходим из режима редактирования
         exitEditMode();

         // Перерисовываем таблицу
         renderBrandsTable();

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
   renderBrandsTable();
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

// Добавить новый бренд
addForm.addEventListener('submit', async function (e) {
   e.preventDefault();

   const name = brandNameInput.value.trim();

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
         // Добавляем новый бренд в локальные данные
         brands.push({
            id: result.id,
            name: name
         });

         // Перерисовываем таблицу
         renderBrandsTable();

         // Очищаем форму
         brandNameInput.value = '';
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
   loadBrands();
});