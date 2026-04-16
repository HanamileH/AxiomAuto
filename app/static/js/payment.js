const paymentForm = document.getElementById("paymentForm");
const paymentStatus = document.getElementById("paymentStatus");
const cardNumberInput = document.getElementById("cardNumber");
const expiryInput = document.getElementById("expiry");
const cvvInput = document.getElementById("cvv");
const submitPaymentBtn = document.getElementById("submitPaymentBtn");

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
  paymentStatus.textContent = message;
  paymentStatus.classList.remove("success", "error");
  paymentStatus.classList.add(type);
}

function setSubmitting(isSubmitting) {
  if (!submitPaymentBtn) {
    return;
  }

  submitPaymentBtn.disabled = isSubmitting;
  submitPaymentBtn.textContent = isSubmitting ? "Обрабатываем..." : "Оплатить";
}

cardNumberInput.addEventListener("input", (event) => {
  cardNumberInput.value = formatCardNumber(event.target.value);
});

expiryInput.addEventListener("input", (event) => {
  expiryInput.value = formatExpiry(event.target.value);
});

cvvInput.addEventListener("input", (event) => {
  cvvInput.value = event.target.value.replace(/\D/g, "").slice(0, 3);
});

paymentForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const paymentPayload = {
    cardNumber: cardNumberInput.value,
    cardHolder: document.getElementById("cardHolder").value.trim(),
    expiry: expiryInput.value,
    cvv: cvvInput.value,
    phoneNumber: document.getElementById("phoneNumber").value.trim(),
    colorId: paymentForm.dataset.colorId,
    paymentType: paymentForm.dataset.paymentType || "bank_online",
  };

  if (paymentPayload.cardNumber.replace(/\s/g, "").length !== 16) {
    showStatus("Ошибка: введите корректный номер карты.", "error");
    return;
  }

  if (paymentPayload.expiry.length !== 5 || !paymentPayload.expiry.includes("/")) {
    showStatus("Ошибка: укажите срок действия в формате MM/YY.", "error");
    return;
  }

  if (paymentPayload.cvv.length !== 3) {
    showStatus("Ошибка: CVV должен содержать 3 цифры.", "error");
    return;
  }

  showStatus("Сервер обрабатывает заказ и ожидает ответ банка...", "success");
  setSubmitting(true);

  try {
    const response = await fetch(paymentForm.dataset.paymentUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(paymentPayload),
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
