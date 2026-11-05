/* ***** Grant select - used by scanner_form_grant_select_option_field.html and grant_select.html ***** */

// Grant dropdowns can open a modal for creating a new grant. When the grant is saved, the
// server sends a "grantCreated" event, and this adds it to the dropdown.

(function () {
  // Loaded by every grant field, and again when htmx re-renders the form.
  // Listeners are on document, so attaching them once covers every grant field:
  if (window.grantSelectInitialised) {
    return;
  }
  window.grantSelectInitialised = true;

  // "Create new ..." in grant dropdowns (event comes from js/forms/select2.js):
  document.addEventListener("select2-action", function (e) {
    const wrapper = e.target.closest(".grant-select");
    if (wrapper && wrapper.dataset.grantCreateUrl) {
      htmx.ajax("GET", wrapper.dataset.grantCreateUrl, {
        target: "#grant-modal-slot",
        values: { field: wrapper.dataset.grantField },
      });
    }
  });

  document.addEventListener("grantCreated", function (e) {
    const select = document.querySelector(`select[name="${CSS.escape(e.detail.field)}"]`);
    if (select) {
      // Old scanner forms: with one choice or none, the dropdown is disabled, and a single
      // choice is sent through a hidden input instead. Now there's a new choice, so use the
      // dropdown:
      const hidden = document.getElementById(`hidden_${e.detail.field}`);
      if (hidden) {
        hidden.remove();
      }
      select.disabled = false;
      // Above the "Create new …" action, if there is one:
      select.add(
        new Option(e.detail.label, e.detail.pk, true, true),
        select.querySelector("option[data-action]")
      );
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
