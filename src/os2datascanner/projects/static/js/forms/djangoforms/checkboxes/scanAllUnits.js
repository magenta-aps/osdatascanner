/***** scanAllUnits.js *****/
// Disables/enables org_units Select2 based on scan_scope_mode ("all" vs "select").
// Used on "create/edit scannerjob" forms.

(() => {
  const selectId = "id_org_units";

  function sync() {
    const selectEl = document.getElementById(selectId);

    const checked = document.querySelector('input[name="scan_scope_mode"]:checked');
    const mode = checked ? checked.value : null;

    if (!selectEl || !mode) {
      return;
    }

    const disable = mode === "all";
    $(selectEl).prop("disabled", disable).trigger("change.select2");
  }

  function init() {
    const radios = document.querySelectorAll('input[name="scan_scope_mode"]');

    if (!radios.length) {
      return;
    }

    sync();
    radios.forEach((r) => {
      r.addEventListener("change", sync);
    });
  }

  document.addEventListener("DOMContentLoaded", init);

  if (window.htmx) {
    window.htmx.onLoad(init);
  }
})();
