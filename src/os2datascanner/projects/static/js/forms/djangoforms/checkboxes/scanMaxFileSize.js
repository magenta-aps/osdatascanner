/***** scanMaxFileSize.js *****/
// Disables/enables NumberInput based on checkbox state.
// Used on "create/edit scannerjob" forms.

(() => {
  function initWidget(wrapper) {
    const toggle = wrapper.querySelector('input[type="checkbox"]');
    const numInput = wrapper.querySelector('input[type="number"]');
    const hidden = wrapper.querySelector('input[type="hidden"]');

    if (!toggle || !numInput || !hidden) {
      return;
    }

    function sync() {
      numInput.disabled = !toggle.checked;
      hidden.disabled = toggle.checked;
    }

    sync();
    toggle.addEventListener("change", sync);
  }

  function init() {
    document.querySelectorAll("[data-scan-max-file-size]").forEach(initWidget);
  }

  document.addEventListener("DOMContentLoaded", init);

  if (window.htmx) {
    window.htmx.onLoad(init);
  }
})();
