const colorButtons = document.querySelectorAll(".color-btn");
const selectedColorName = document.getElementById("selectedColorName");
const selectedColorInput = document.getElementById("selectedColorInput");
const purchaseBtn = document.getElementById("purchaseBtn");

function selectColor(button) {
  const colorName = button.dataset.colorName;

  colorButtons.forEach((item) => {
    item.classList.remove("selected");
    item.setAttribute("aria-pressed", "false");
  });

  button.classList.add("selected");
  button.setAttribute("aria-pressed", "true");

  selectedColorName.textContent = colorName;
  selectedColorInput.value = colorName;
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
