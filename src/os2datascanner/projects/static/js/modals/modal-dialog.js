/* ***** Shared modal dialog behaviour - used by modal-dialog.html ***** */

// Open:  <button data-open-modal="<modal id>">
// Close: any [data-close-modal] inside the modal, a click on the backdrop, or Esc (native).

(function () {
  // Loaded by the component, so it runs once per modal and after every htmx swap.
  // The listeners are on document, so attaching them once covers every modal:
  if (window.modalDialogInitialised) {
    return;
  }
  window.modalDialogInitialised = true;

  function isBackdropClick(modal, e) {
    const rect = modal.getBoundingClientRect();
    return e.clientX < rect.left || e.clientX > rect.right ||
      e.clientY < rect.top || e.clientY > rect.bottom;
  }

  document.addEventListener("click", function (e) {
    const opener = e.target.closest("[data-open-modal]");
    if (opener) {
      const modal = document.getElementById(opener.dataset.openModal);
      if (modal && !modal.open) {
        modal.showModal();
      }
      return;
    }

    const closer = e.target.closest("[data-close-modal]");
    if (closer) {
      const modal = closer.closest("dialog");
      if (modal) {
        modal.close();
      }
      return;
    }

    // Clicks on the backdrop and on the dialog's own empty area both target the
    // <dialog> itself, so check whether the click was outside its box:
    if (e.target instanceof HTMLDialogElement && e.target.open && isBackdropClick(e.target, e)) {
      e.target.close();
    }
  });
})();
