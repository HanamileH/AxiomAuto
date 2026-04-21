const terminalForm = document.getElementById("terminalPaymentForm");
const paymentStatus = document.getElementById("terminalPaymentStatus");
const submitBtn = document.getElementById("submitTerminalPaymentBtn");

const cardNumberInput = document.getElementById("cardNumber");
const cardHolderInput = document.getElementById("cardHolder");
const expiryInput = document.getElementById("expiry");
const cvvInput = document.getElementById("cvv");

let basePayload = null;

function formatCardNumber(value) {
  return value
    .replace(/\D/g, "")
    .slice(0, 16)
    .replace(/(\d{4})(?=\d)/g, "$1 ");
}

function formatExpiry(value) {
  const digitsOnly = value.replace(/\D/g, "").slice(0, 4);
  if (digitsOnly.length <= 2) {
    return digitsOnly;
  }
  return `${digitsOnly.slice(0, 2)}/${digitsOnly.slice(2)}`;
}

function showStatus(message, type) {
  if (!paymentStatus) {
    return;
  }
  paymentStatus.textContent = message;
  paymentStatus.classList.remove("success", "error");
  paymentStatus.classList.add(type);
}

function setSubmitting(isSubmitting) {
  if (!submitBtn) {
    return;
  }
  submitBtn.disabled = isSubmitting;
  submitBtn.textContent = isSubmitting ? "Обрабатываем..." : "Оплатить";
}

if (cardNumberInput) {
  cardNumberInput.addEventListener("input", (event) => {
    cardNumberInput.value = formatCardNumber(event.target.value);
  });
}

if (expiryInput) {
  expiryInput.addEventListener("input", (event) => {
    expiryInput.value = formatExpiry(event.target.value);
  });
}

if (cvvInput) {
  cvvInput.addEventListener("input", (event) => {
    cvvInput.value = event.target.value.replace(/\D/g, "").slice(0, 3);
  });
}

window.addEventListener("message", (event) => {
  if (event.origin !== window.location.origin) {
    return;
  }

  const data = event.data || {};
  if (data.type !== "axiom-terminal-init") {
    return;
  }

  if (!data.payload || data.payload.paymentType !== "bank_terminal") {
    showStatus("Ошибка: не удалось получить данные заказа.", "error");
    return;
  }

  if (String(data.payload.colorId) !== String(terminalForm.dataset.colorId)) {
    showStatus("Ошибка: данные заказа не соответствуют выбранной комплектации.", "error");
    return;
  }

  basePayload = data.payload;
  showStatus("Данные заказа получены. Введите данные карты и нажмите «Оплатить».", "success");
  if (submitBtn) {
    submitBtn.disabled = false;
  }
});

terminalForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (!basePayload) {
    showStatus("Ошибка: данные заказа не получены из основного окна.", "error");
    return;
  }

  const payload = {
    ...basePayload,
    paymentType: "bank_terminal",
    cardNumber: cardNumberInput?.value || "",
    cardHolder: (cardHolderInput?.value || "").trim(),
    expiry: expiryInput?.value || "",
    cvv: cvvInput?.value || "",
  };

  if (payload.cardNumber.replace(/\s/g, "").length !== 16) {
    showStatus("Ошибка: введите корректный номер карты.", "error");
    return;
  }

  if (payload.expiry.length !== 5 || !payload.expiry.includes("/")) {
    showStatus("Ошибка: укажите срок действия в формате MM/YY.", "error");
    return;
  }

  if (payload.cvv.length !== 3) {
    showStatus("Ошибка: CVV должен содержать 3 цифры.", "error");
    return;
  }

  showStatus("Отправляем запрос в банк...", "success");
  setSubmitting(true);

  try {
    const response = await fetch(terminalForm.dataset.paymentUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok || data.status !== "success") {
      throw new Error(data.error_text || "Не удалось обработать оплату.");
    }

    window.location.href = data.redirect_url;
  } catch (error) {
    showStatus(error.message || "Произошла ошибка при оплате.", "error");
    setSubmitting(false);
  }
});

