/* ***** Shared modal dialog behaviour - used by modal-dialog.html ***** */

// Open:  <button data-open-modal="<modal id>">, or data-open-on-load on a modal that htmx inserts.
// Close: any [data-close-modal] inside the modal, a click on the backdrop, or Esc (native).

(function () {
  const OPEN_ON_LOAD = "dialog[data-open-on-load]:not([open])";

  // While a modal is open, the rest of the page is inert and drawn underneath it, so the snackbars
  // are moved into the modal. As a popover, the container is drawn on top of the modal and placed
  // against the viewport, rather than against the modal itself:
  function openModal(modal) {
    modal.showModal();

    const snackbars = document.getElementById("snackbar");
    if (snackbars) {
      snackbars.popover = "manual";
      modal.append(snackbars);
      snackbars.showPopover();
    }
  }

  // NOTE: htmx runs scripts it inserts once they've loaded (which can be after the modal itself
  // has been inserted).
  // Open any modal that's already waiting, every time this runs:
  document.querySelectorAll(OPEN_ON_LOAD).forEach(openModal);

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
        openModal(modal);
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

  // NOTE: htmx fires "htmx:load" on each element it inserts.
  // Open any modal with data-open-on-load, whether it's the inserted element itself or inside it:
  document.addEventListener("htmx:load", function (e) {
    const modal = e.target.matches(OPEN_ON_LOAD) ? e.target : e.target.querySelector(OPEN_ON_LOAD);
    if (modal) {
      openModal(modal);
    }
  });

  // Move any snackbars back out when a modal closes, however it's closed.
  // NOTE: "close" doesn't bubble, so this listens in the capture phase:
  document.addEventListener("close", function (e) {
    const snackbars = document.getElementById("snackbar");
    if (snackbars && snackbars.parentElement === e.target) {
      snackbars.removeAttribute("popover");
      document.body.prepend(snackbars);
    }
  }, true);
})();
