/* ***** Distribute results modal - used by modal__distribute-results.html ***** */

(function () {
    // Loaded by the modal, so it runs again whenever filters or pagination swap it with htmx.
    // The listeners are on document, so attaching them once covers the re-rendered modal:
    if (window.distributeModalInitialised) {
        return;
    }
    window.distributeModalInitialised = true;

    function distributeAnyChecked() {
        return !!document.querySelector("input[name='distribute-to']:checked");
    }

    function updateDistributeActionButtons() {
        // Only allow releasing or clearing when at least one scannerjob is selected:
        const hasSelection = distributeAnyChecked();
        const releaseBtn = document.getElementById("distribute-matches");
        const clearBtn = document.getElementById("clear-distribute-selection");
        if (releaseBtn) {
            releaseBtn.disabled = !hasSelection;
        }
        if (clearBtn) {
            clearBtn.disabled = !hasSelection;
        }
    }

    // Filter the scannerjob list by the search query:
    document.addEventListener("input", function (e) {
        if (e.target.id !== "search-bar") {
            return;
        }
        const query = e.target.value.toLowerCase();
        const scannerJobList = document.getElementById("scannerjob-list");

        for (const scannerJob of scannerJobList.children) {
            const scannerJobName = scannerJob.innerHTML.toLowerCase();
            if (scannerJobName.includes(query)) {
                scannerJob.style.display = 'block';
            } else {
                scannerJob.style.display = 'none';
            }
        }
    });

    document.addEventListener("change", function (e) {
        if (e.target.matches("input[name='distribute-to']")) {
            updateDistributeActionButtons();
        }
    });

    document.addEventListener("click", function (e) {
        if (e.target.closest("#clear-distribute-selection")) {
            document.querySelectorAll("input[name='distribute-to']:checked")
                .forEach(function (cb) { cb.checked = false; });
            updateDistributeActionButtons();
        }
    });
})();
