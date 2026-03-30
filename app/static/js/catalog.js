const filters = {
  brand: document.getElementById("filter-brand"),
  model: document.getElementById("filter-model"),
  yearFrom: document.getElementById("filter-year-from"),
  yearTo: document.getElementById("filter-year-to"),
  priceFrom: document.getElementById("filter-price-from"),
  priceTo: document.getElementById("filter-price-to"),
  engineType: document.getElementById("filter-engine-type"),
  transmission: document.getElementById("filter-transmission"),
  engineVolumeMin: document.getElementById("filter-engine-volume-min"),
  enginePowerMin: document.getElementById("filter-engine-power-min"),
};

const catalogList = document.getElementById("catalog-list");

function collectFilterParams() {
  const params = new URLSearchParams();

  if (filters.brand.value.trim()) params.set("brand", filters.brand.value.trim());
  if (filters.model.value.trim()) params.set("model", filters.model.value.trim());
  if (filters.yearFrom.value) params.set("year_from", filters.yearFrom.value);
  if (filters.yearTo.value) params.set("year_to", filters.yearTo.value);
  if (filters.priceFrom.value) params.set("price_from", filters.priceFrom.value);
  if (filters.priceTo.value) params.set("price_to", filters.priceTo.value);
  if (filters.engineType.value) params.set("engine_type", filters.engineType.value);
  if (filters.transmission.value) params.set("transmission", filters.transmission.value);
  if (filters.engineVolumeMin.value) params.set("engine_volume_min", filters.engineVolumeMin.value);
  if (filters.enginePowerMin.value) params.set("engine_power_min", filters.enginePowerMin.value);

  return params;
}

async function updateCatalog() {
  const params = collectFilterParams();
  const response = await fetch(`/catalog/filter?${params.toString()}`);

  if (!response.ok) {
    return;
  }

  const data = await response.json();
  catalogList.innerHTML = data.html;
}

function debounce(callback, delay) {
  let timer = null;

  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => callback(...args), delay);
  };
}

const debouncedUpdate = debounce(updateCatalog, 250);

Object.values(filters).forEach((filter) => {
  const eventName = filter.tagName.toLowerCase() === "select" ? "change" : "input";
  filter.addEventListener(eventName, debouncedUpdate);
});
