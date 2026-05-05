function showOverview(row, toggleButton) {

  let overviewRow = row.nextElementSibling;
  toggleClass(toggleButton, "up");
  let buttonOpen = hasClass(toggleButton, "up");

  overviewRow.hidden = !buttonOpen;
}

document.addEventListener("DOMContentLoaded",
  () => {
    htmx.onLoad(function (content) {
      if (hasClass(content, "content") || hasClass(content, "page") || hasClass(content, "employee_row")) {

        let expandButtons = content.querySelectorAll(".overview-expand");

        expandButtons.forEach(element => {
          element.addEventListener("click", function (e) {
            targ = e.target;
            let row = closestElement(targ, "tr");
            showOverview(row, targ);
          });
        });

        // Reset dependent filters when a parent filter changes so stale values
        // are not carried over to requests where they are no longer valid.
        const orgUnitSelect = content.querySelector("#org_units");
        const scannerjobSelect = content.querySelector("#scannerjobs");
        const sourceTypeSelect = content.querySelector("#source_type");

        if (orgUnitSelect && scannerjobSelect) {
          orgUnitSelect.addEventListener("change", function () {
            scannerjobSelect.value = "all";
            if (sourceTypeSelect) { sourceTypeSelect.value = "all"; }
          });
        }
        if (scannerjobSelect && sourceTypeSelect) {
          scannerjobSelect.addEventListener("change", function () {
            sourceTypeSelect.value = "all";
          });
        }
      }
    });
  }
);
