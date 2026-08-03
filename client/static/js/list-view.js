document.addEventListener("DOMContentLoaded", () => {
  const toggles = document.querySelectorAll(".mx-view-toggle[data-list-target]");

  toggles.forEach((toggle) => {
    const listId = toggle.dataset.listTarget;
    const container = document.querySelector(`.mx-list-container[data-list-id="${listId}"]`);
    if (!container) return;

    const storageKey = "mx-list-view:" + listId;
    const savedView = localStorage.getItem(storageKey);
    if (savedView) {
      container.dataset.view = savedView;
    }

    const buttons = toggle.querySelectorAll("[data-view-btn]");

    const syncActiveButton = () => {
      buttons.forEach((b) => {
        b.classList.toggle("active", b.dataset.viewBtn === container.dataset.view);
      });
    };
    syncActiveButton();

    buttons.forEach((btn) => {
      btn.addEventListener("click", () => {
        container.dataset.view = btn.dataset.viewBtn;
        localStorage.setItem(storageKey, btn.dataset.viewBtn);
        syncActiveButton();
      });
    });
  });
});