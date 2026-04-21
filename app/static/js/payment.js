const paymentForm = document.getElementById("paymentForm");
const paymentStatus = document.getElementById("paymentStatus");
const submitPaymentBtn = document.getElementById("submitPaymentBtn");

const selfBuyerBlock = document.getElementById("selfBuyerBlock");
const clientBuyerBlock = document.getElementById("clientBuyerBlock");
const selfPaymentBlock = document.getElementById("selfPaymentBlock");
const clientPaymentBlock = document.getElementById("clientPaymentBlock");
const terminalHint = document.getElementById("terminalHint");

const phoneNumberInput = document.getElementById("phoneNumber");

const cardNumberInput = document.getElementById("cardNumber");
const cardHolderInput = document.getElementById("cardHolder");
const expiryInput = document.getElementById("expiry");
const cvvInput = document.getElementById("cvv");

const clientNameInput = document.getElementById("clientName");
const clientSurnameInput = document.getElementById("clientSurname");
const clientPatronymicInput = document.getElementById("clientPatronymic");

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
  if (!submitPaymentBtn) {
    return;
  }

  submitPaymentBtn.disabled = isSubmitting;
  submitPaymentBtn.textContent = isSubmitting ? "Обрабатываем..." : "Оплатить";
}

function getOrderFor() {
  const selected = document.querySelector('input[name="orderFor"]:checked');
  if (selected) {
    return selected.value;
  }

  const hidden = document.querySelector('input[name="orderFor"][type="hidden"]');
  return hidden ? hidden.value : "self";
}

function getClientPaymentType() {
  const selected = document.querySelector('input[name="clientPaymentType"]:checked');
  return selected ? selected.value : "cash";
}

function setRequired(input, isRequired) {
  if (!input) {
    return;
  }
  input.required = isRequired;
  input.disabled = !isRequired && input.id !== "clientPatronymic";
}

function setEnabled(input, isEnabled) {
  if (!input) {
    return;
  }
  input.disabled = !isEnabled;
  input.required = isEnabled;
}

function toggleView() {
  const orderFor = getOrderFor();

  const isClient = orderFor === "client";

  if (selfBuyerBlock) selfBuyerBlock.classList.toggle("hidden", isClient);
  if (clientBuyerBlock) clientBuyerBlock.classList.toggle("hidden", !isClient);
  if (selfPaymentBlock) selfPaymentBlock.classList.toggle("hidden", isClient);
  if (clientPaymentBlock) clientPaymentBlock.classList.toggle("hidden", !isClient);

  if (clientNameInput) clientNameInput.required = isClient;
  if (clientSurnameInput) clientSurnameInput.required = isClient;
  if (clientPatronymicInput) clientPatronymicInput.required = false;

  setEnabled(cardNumberInput, !isClient);
  setEnabled(cardHolderInput, !isClient);
  setEnabled(expiryInput, !isClient);
  setEnabled(cvvInput, !isClient);

  const paymentType = getClientPaymentType();
  if (terminalHint) {
    terminalHint.classList.toggle("hidden", !isClient || paymentType !== "bank_terminal");
  }
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

document.querySelectorAll('input[name="orderFor"]').forEach((radio) => {
  radio.addEventListener("change", toggleView);
});

document.querySelectorAll('input[name="clientPaymentType"]').forEach((radio) => {
  radio.addEventListener("change", toggleView);
});

toggleView();

paymentForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const orderFor = getOrderFor();
  const phoneNumber = (phoneNumberInput?.value || "").trim();

  const basePayload = {
    orderFor,
    phoneNumber,
    colorId: paymentForm.dataset.colorId,
  };

  if (orderFor === "client") {
    const paymentType = getClientPaymentType();
    const clientPayload = {
      clientName: (clientNameInput?.value || "").trim(),
      clientSurname: (clientSurnameInput?.value || "").trim(),
      clientPatronymic: (clientPatronymicInput?.value || "").trim(),
    };

    if (!clientPayload.clientName || !clientPayload.clientSurname) {
      showStatus("Ошибка: укажите имя и фамилию клиента.", "error");
      return;
    }

    if (paymentType === "bank_terminal") {
      const terminalUrl = paymentForm.dataset.terminalUrl;
      if (!terminalUrl) {
        showStatus("Ошибка: не удалось открыть страницу терминала.", "error");
        return;
      }

      const terminalWindow = window.open(
        `${terminalUrl}?color=${encodeURIComponent(paymentForm.dataset.colorId)}`,
        "_blank",
      );

      if (!terminalWindow) {
        showStatus("Ошибка: браузер заблокировал открытие окна терминала.", "error");
        return;
      }

      const payload = {
        ...basePayload,
        ...clientPayload,
        paymentType,
      };

      const sendPayload = () => {
        try {
          terminalWindow.postMessage(
            { type: "axiom-terminal-init", payload },
            window.location.origin,
          );
        } catch {
          // ignore
        }
      };

      const intervalId = window.setInterval(sendPayload, 250);
      window.setTimeout(() => window.clearInterval(intervalId), 4000);

      showStatus("Окно терминала открыто. Завершите оплату в новом окне.", "success");
      return;
    }

    const payload = {
      ...basePayload,
      ...clientPayload,
      paymentType: paymentType || "cash",
    };

    showStatus("Оформляем заказ...", "success");
    setSubmitting(true);

    try {
      const response = await fetch(paymentForm.dataset.paymentUrl, {
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

    return;
  }

  const paymentPayload = {
    ...basePayload,
    paymentType: "bank_online",
    cardNumber: cardNumberInput?.value || "",
    cardHolder: (cardHolderInput?.value || "").trim(),
    expiry: expiryInput?.value || "",
    cvv: cvvInput?.value || "",
  };

  if (paymentPayload.cardNumber.replace(/\s/g, "").length !== 16) {
    showStatus("Ошибка: введите корректный номер карты.", "error");
    return;
  }

  if (
    paymentPayload.expiry.length !== 5 ||
    !paymentPayload.expiry.includes("/")
  ) {
    showStatus("Ошибка: укажите срок действия в формате MM/YY.", "error");
    return;
  }

  if ((paymentPayload.cvv || "").length !== 3) {
    showStatus("Ошибка: CVV должен содержать 3 цифры.", "error");
    return;
  }

  showStatus("Сервер обрабатывает заказ и ожидает ответ банка...", "success");
  setSubmitting(true);

  try {
    const response = await fetch(paymentForm.dataset.paymentUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
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
