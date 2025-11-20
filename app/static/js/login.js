document.getElementById("btn-login").addEventListener("click", async () => {
    const errorBox = document.getElementById("error-box");
    errorBox.style.display = "none";
    errorBox.innerText = "";

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    // Проверяем обязательные поля
    if (!email || !password) {
        showError("Введите электронную почту и пароль.");
        return;
    }

    // Отправляем запрос
    let response;
    try {
        response = await fetch("/login", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ email, password })
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

    // Успешная авторизация
    window.location.href = "/profile";
});

function showError(text) {
    const box = document.getElementById("error-box");
    box.style.display = "block";
    box.innerText = text;
}

function convertError(code) {
    const map = {
        "empty email": "Введите электронную почту.",
        "empty password": "Введите пароль.",
        "email or password is incorrect": "Неверная электронная почта или пароль.",
        "unknown error": "Неизвестная ошибка. Повторите попытку."
    };

    return map[code] || "Ошибка: " + code;
}
