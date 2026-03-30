(() => {
  function parseValue(rawValue, type) {
    const value = (rawValue || "").trim();

    if (type === "number") {
      const normalized = value.replace(/\s+/g, "").replace(",", ".");
      const parsed = Number.parseFloat(normalized);
      return Number.isNaN(parsed) ? Number.NEGATIVE_INFINITY : parsed;
    }

    if (type === "date") {
      const timestamp = Date.parse(value);
      return Number.isNaN(timestamp) ? Number.NEGATIVE_INFINITY : timestamp;
    }

    return value.toLowerCase();
  }

  function initSortableTable(table) {
    if (!table || table.dataset.sortInitialized === "1") return;

    const headers = Array.from(table.querySelectorAll("thead th"));
    const sortableHeaders = headers.filter((header) => header.dataset.sortKey);
    if (!sortableHeaders.length) return;

    const tbody = table.querySelector("tbody");
    if (!tbody) return;

    const sortState = { key: null, direction: "asc", isApplying: false };

    const getCellByKey = (row, key, fallbackIndex) => {
      return (
        row.querySelector(`[data-sort-key="${key}"]`) ||
        row.children[fallbackIndex] ||
        null
      );
    };

    const getSortValue = (row, key, type, fallbackIndex) => {
      const cell = getCellByKey(row, key, fallbackIndex);
      if (!cell) return type === "number" || type === "date" ? Number.NEGATIVE_INFINITY : "";

      const explicitValue = cell.dataset.sortValue;
      const textValue = explicitValue !== undefined ? explicitValue : cell.textContent || "";
      return parseValue(textValue, type);
    };

    const applySort = (key, direction) => {
      if (!key || sortState.isApplying) return;

      const activeHeader = headers.find((header) => header.dataset.sortKey === key);
      if (!activeHeader) return;

      const sortType = activeHeader.dataset.sortType || "string";
      const secondaryKey = activeHeader.dataset.sortSecondary || "";
      const columnIndex = headers.indexOf(activeHeader);
      const secondaryHeader = headers.find((header) => header.dataset.sortKey === secondaryKey);
      const secondaryType = secondaryHeader?.dataset.sortType || "string";
      const secondaryIndex = secondaryHeader ? headers.indexOf(secondaryHeader) : -1;

      sortState.isApplying = true;

      const rows = Array.from(tbody.querySelectorAll("tr"));
      rows.sort((a, b) => {
        const aValue = getSortValue(a, key, sortType, columnIndex);
        const bValue = getSortValue(b, key, sortType, columnIndex);

        if (aValue < bValue) return direction === "asc" ? -1 : 1;
        if (aValue > bValue) return direction === "asc" ? 1 : -1;

        if (secondaryKey) {
          const aSecondary = getSortValue(a, secondaryKey, secondaryType, secondaryIndex);
          const bSecondary = getSortValue(b, secondaryKey, secondaryType, secondaryIndex);
          if (aSecondary < bSecondary) return direction === "asc" ? -1 : 1;
          if (aSecondary > bSecondary) return direction === "asc" ? 1 : -1;
        }

        return 0;
      });

      tbody.append(...rows);

      headers.forEach((header) => {
        header.classList.remove("sort-asc", "sort-desc", "sort-active");
      });
      activeHeader.classList.add("sort-active", direction === "asc" ? "sort-asc" : "sort-desc");
      sortState.key = key;
      sortState.direction = direction;
      sortState.isApplying = false;
    };

    sortableHeaders.forEach((header) => {
      header.classList.add("sortable-header");
      const indicator = document.createElement("span");
      indicator.className = "sort-indicator";
      indicator.textContent = "↕";
      header.appendChild(indicator);

      header.addEventListener("click", () => {
        const isSameKey = sortState.key === header.dataset.sortKey;
        const nextDirection = isSameKey && sortState.direction === "asc" ? "desc" : "asc";
        applySort(header.dataset.sortKey, nextDirection);
      });
    });

    const observer = new MutationObserver((mutations) => {
      if (sortState.isApplying || !sortState.key) return;
      const hasRowChanges = mutations.some((mutation) => mutation.type === "childList");
      if (hasRowChanges) {
        applySort(sortState.key, sortState.direction);
      }
    });

    observer.observe(tbody, { childList: true, subtree: false });
    table.dataset.sortInitialized = "1";
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("table.entity-table").forEach(initSortableTable);
  });
})();
