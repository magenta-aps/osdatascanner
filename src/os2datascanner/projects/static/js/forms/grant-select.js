/* ***** Grant select - used by scanner_form_grant_select_option_field.html ***** */

// The "+" next to a grant dropdown loads a modal for creating a new grant. When the grant
// is saved, the server sends a "grantCreated" event, and this adds it to the dropdown.

(function () {
  // Loaded by every grant field, and again when htmx re-renders the form.
  // The listener is on document, so attaching it once covers every grant field:
  if (window.grantSelectInitialised) {
    return;
  }
  window.grantSelectInitialised = true;

  document.addEventListener("grantCreated", function (e) {
    const select = document.querySelector(`select[name="${CSS.escape(e.detail.field)}"]`);
    if (select) {
      // With one choice or none, the dropdown is disabled, and a single choice is sent
      // through a hidden input instead. Now there's a new choice, so use the dropdown:
      const hidden = document.getElementById(`hidden_${e.detail.field}`);
      if (hidden) {
        hidden.remove();
      }
      select.disabled = false;
      select.add(new Option(e.detail.label, e.detail.pk, true, true));
      select.dispatchEvent(new Event("change", { bubbles: true }));
    }

    // The event fires on the modal's form:
    const modal = e.target.closest("dialog");
    if (modal) {
      // Removed once it's closed, so modal-dialog.js has moved the snackbars out of it first:
      modal.addEventListener("close", () => modal.remove(), { once: true });
      modal.close();
    }
  });
})();
