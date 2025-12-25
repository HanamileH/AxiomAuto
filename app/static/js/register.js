document.getElementById("btn-auth").addEventListener("click", async () => {
  const errorBox = document.getElementById("error-box");
  errorBox.style.display = "none";
  errorBox.innerText = "";

  const name = document.getElementById("name").value.trim();
  const surname = document.getElementById("surname").value.trim();
  const patronymic = document.getElementById("patronymic").value.trim();
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value.trim();
  const confirmPassword = document
    .getElementById("confirm-password")
    .value.trim();

  // Токен hCaptcha
  const hcaptchaResponse = hcaptcha.getResponse();

  if (!hcaptchaResponse) {
    showError("Пожалуйста, подтвердите, что вы не робот.");
    return;
  }

  // Проверяем обязательные поля
  if (!name || !surname || !email || !password || !confirmPassword) {
    showError("Заполните все обязательные поля.");
    return;
  }

  if (password !== confirmPassword) {
    showError("Пароли не совпадают.");
    return;
  }

  // Отправляем запрос
  let response;
  try {
    response = await fetch("/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name,
        surname,
        patronymic,
        email,
        password,
        "hcaptcha_response": hcaptchaResponse,
      }),
    });
  } catch (e) {
    showError("Ошибка соединения с сервером.");
    return;
  }

  const result = await response.json();

  if (result.status === "error") {
    showError(convertError(result.error_text));
    return;
  }

  // Успешная регистрация
  window.location.href = "/profile";
});

function showError(text) {
  const errorBox = document.getElementById("error-box");
  errorBox.style.display = "block";
  errorBox.innerText = text;
}

// Преобразование ошибок системы в понятные сообщения
function convertError(code) {
  const map = {
    "empty name": "Введите имя.",
    "invalid name length": "Недопустимая длина имени.",
    "invalid name format": "Неверный формат имени.",

    "empty surname": "Введите фамилию.",
    "invalid surname length": "Недопустимая длина фамилии.",
    "invalid surname format": "Неверный формат фамилии.",

    "invalid patronymic length": "Недопустимая длина отчества.",
    "invalid patronymic format": "Неверный формат отчества.",

    "empty email": "Введите электронную почту.",
    "invalid email length": "Недопустимая длина электронной почты.",
    "invalid email format": "Формат электронной почты неверен.",

    "empty password": "Введите пароль.",
    "invalid password length": "Недопустимая длина пароля.",

    "this email already exists": "Этот email уже зарегистрирован.",

    "unknown error": "Неизвестная ошибка. Повторите попытку.",

    "incorrect captcha": "Пожалуйста, подтвердите, что вы не робот."
  };

  return map[code] || "Ошибка: " + code;
}
