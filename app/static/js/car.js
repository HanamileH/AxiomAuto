const colorButtons = document.querySelectorAll(".color-btn");
const selectedColorName = document.getElementById("selectedColorName");
const selectedColorInput = document.getElementById("selectedColorInput");
const purchaseBtn = document.getElementById("purchaseBtn");
purchaseBtn.disabled = true; // Отключена по умолчанию т.к. не выбран цвет

function selectColor(button) {
  const colorName = button.dataset.colorName;
  const colorId = button.dataset.colorId;

  colorButtons.forEach((item) => {
    item.classList.remove("selected");
    item.setAttribute("aria-pressed", "false");
  });

  button.classList.add("selected");
  button.setAttribute("aria-pressed", "true");

  selectedColorName.textContent = colorName;
  selectedColorInput.value = colorId;
  purchaseBtn.disabled = false;
}

colorButtons.forEach((button) => {
  button.setAttribute("aria-pressed", "false");

  if (button.disabled) {
    return;
  }

  button.addEventListener("click", () => {
    selectColor(button);
  });
});

if (!Array.from(colorButtons).some((button) => !button.disabled)) {
  purchaseBtn.disabled = true;
}
