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

        // Reset source_type when scannerjob changes so a stale value is not
        // carried over to requests where it is no longer valid.
        const scannerjobSelect = content.querySelector("#scannerjobs");
        const sourceTypeSelect = content.querySelector("#source_type");
        if (scannerjobSelect && sourceTypeSelect) {
          scannerjobSelect.addEventListener("change", function () {
            sourceTypeSelect.value = "all";
          });
        }
      }
    });
  }
);
