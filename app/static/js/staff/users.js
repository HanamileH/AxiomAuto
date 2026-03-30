let objects = [];
let editMode = false;
let currentEditId = null;

const objectTableBody = document.getElementById("objectsTableBody");
const addForm = document.getElementById("addObjectForm");
const errorMessage = document.getElementById("errorMessage");

const nameInput = document.getElementById("userName");
const surnameInput = document.getElementById("userSurname");
const patronymicInput = document.getElementById("userPatronymic");
const emailInput = document.getElementById("userEmail");
const passwordInput = document.getElementById("userPassword");
const roleInput = document.getElementById("userRole");

const ROLE_TITLES = {
  user: "Пользователь",
  manager: "Менеджер",
  admin: "Администратор",
};

function showError(message) {
  errorMessage.textContent = message;
  errorMessage.style.display = "block";
}

function hideError() {
  errorMessage.style.display = "none";
}

async function loadObjects() {
  try {
    const response = await fetch("/api/crud/users");
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

  objects.forEach((user) => {
    const row = document.createElement("tr");
    row.id = `object-row-${user.id}`;
    row.innerHTML = `
      <td>${user.name || ""}</td>
      <td>${user.surname || ""}</td>
      <td>${user.patronymic || ""}</td>
      <td class="hide-data">${user.email || ""}</td>
      <td>${ROLE_TITLES[user.role] || user.role}</td>
      <td><button class="btn-outline edit-btn" data-id="${user.id}">Изменить</button></td>
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

  const user = objects.find((u) => u.id === id);
  if (!user) return;

  currentEditId = id;
  editMode = true;

  const row = document.getElementById(`object-row-${id}`);
  const editRow = document.createElement("tr");
  editRow.id = `edit-row-${id}`;
  editRow.classList.add("edit-panel");
  editRow.innerHTML = `
    <td colspan="6">
      <div class="edit-form-grid" style="display:grid;grid-template-columns:repeat(3,minmax(180px,1fr));gap:12px;">
        <input type="text" id="edit-name-${id}" class="edit-input" value="${user.name || ""}">
        <input type="text" id="edit-surname-${id}" class="edit-input" value="${user.surname || ""}">
        <input type="text" id="edit-patronymic-${id}" class="edit-input" value="${user.patronymic || ""}">
        <input type="email" id="edit-email-${id}" class="edit-input" value="${user.email || ""}">
        <select id="edit-role-${id}" class="edit-input">
          <option value="user" ${user.role === "user" ? "selected" : ""}>Пользователь</option>
          <option value="manager" ${user.role === "manager" ? "selected" : ""}>Менеджер</option>
          <option value="admin" ${user.role === "admin" ? "selected" : ""}>Администратор</option>
        </select>
        <input type="password" id="edit-new-password-${id}" class="edit-input" placeholder="Новый пароль">
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

  document.getElementById(`btn-save-${id}`).addEventListener("click", saveObject);
  document.getElementById(`btn-cancel-${id}`).addEventListener("click", cancelEdit);
  document.getElementById(`btn-delete-${id}`).addEventListener("click", deleteObject);
}

async function saveObject() {
  if (!currentEditId) return;

  const user = objects.find((u) => u.id === currentEditId);
  if (!user) return;

  const name = document.getElementById(`edit-name-${currentEditId}`).value.trim();
  const surname = document.getElementById(`edit-surname-${currentEditId}`).value.trim();
  const patronymic = document.getElementById(`edit-patronymic-${currentEditId}`).value.trim();
  const email = document.getElementById(`edit-email-${currentEditId}`).value.trim();
  const role = document.getElementById(`edit-role-${currentEditId}`).value;
  const newPassword = document.getElementById(`edit-new-password-${currentEditId}`).value;

  if (!name || !surname || !email || !role) {
    showError("Заполните обязательные поля");
    return;
  }

  if (role !== user.role) {
    if (!confirm("Вы действительно хотите изменить уровень доступа пользователя?")) {
      return;
    }
  }

  if (newPassword.trim()) {
    if (!confirm("Вы действительно хотите изменить пароль пользователя?")) {
      return;
    }
  }

  try {
    const response = await fetch(`/api/crud/users/${currentEditId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name,
        surname,
        patronymic,
        email,
        role,
        new_password: newPassword,
      }),
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

  if (!confirm("Внимание: пользователь будет удалён без возможности восстановления. Продолжить?")) {
    return;
  }

  try {
    const response = await fetch(`/api/crud/users/${currentEditId}`, {
      method: "DELETE",
    });

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

addForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const name = nameInput.value.trim();
  const surname = surnameInput.value.trim();
  const patronymic = patronymicInput.value.trim();
  const email = emailInput.value.trim();
  const password = passwordInput.value;
  const role = roleInput.value;

  if (!name || !surname || !email || !password || !role) {
    showError("Заполните обязательные поля");
    return;
  }

  try {
    const response = await fetch("/api/crud/users", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, surname, patronymic, email, password, role }),
    });

    const result = await response.json();

    if (result.success) {
      addForm.reset();
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
