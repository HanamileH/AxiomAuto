const paymentForm = document.getElementById("paymentForm");
const paymentStatus = document.getElementById("paymentStatus");
const cardNumberInput = document.getElementById("cardNumber");
const expiryInput = document.getElementById("expiry");
const cvvInput = document.getElementById("cvv");
const selectedColorLabel = document.getElementById("selectedColorLabel");

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

function mockPaymentService(cardData) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const digits = cardData.cardNumber.replace(/\s/g, "");
      const lastDigit = Number(digits.at(-1));

      if (!Number.isNaN(lastDigit) && lastDigit % 2 === 0) {
        resolve();
      } else {
        reject(new Error("Оплата отклонена"));
      }
    }, 900);
  });
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

  const cardData = {
    cardNumber: cardNumberInput.value,
    cardHolder: document.getElementById("cardHolder").value.trim(),
    expiry: expiryInput.value,
    cvv: cvvInput.value,
    color: selectedColorLabel ? selectedColorLabel.textContent.trim() : "Не выбран",
  };

  if (cardData.cardNumber.replace(/\s/g, "").length !== 16) {
    showStatus("Ошибка: введите корректный номер карты.", "error");
    return;
  }

  if (cardData.expiry.length !== 5 || !cardData.expiry.includes("/")) {
    showStatus("Ошибка: укажите срок действия в формате MM/YY.", "error");
    return;
  }

  if (cardData.cvv.length !== 3) {
    showStatus("Ошибка: CVV должен содержать 3 цифры.", "error");
    return;
  }

  showStatus("Проверяем оплату...", "success");

  try {
    await mockPaymentService(cardData);
    showStatus("Успешно! Оплата автомобиля подтверждена.", "success");
  } catch (error) {
    showStatus("Ошибка оплаты. Проверьте данные карты и попробуйте снова.", "error");
  }
});
