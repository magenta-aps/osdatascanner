function setDropdownEvent() {
  Array.prototype.forEach.call(document.querySelectorAll('.dropdown > select'), function (dropdown) {
    dropdown.addEventListener('change', function (e) {
      if (e.target.hasAttribute('data-autosubmit')) {
        var form = e.target.form;
        if (form) {
          form.submit();
        }
      }
    });
  });
}

function clearFilter(elementid) { // jshint ignore:line
  var element = document.querySelector('#' + elementid + ' [value="all"]').selected = true;
  document.getElementById("filter_form", element).submit();
}
function retentionCheckedBox() {
  const checkbox = document.getElementById('retention-toggle');
  const retention = document.getElementById('retention');
  if (checkbox.checked) {
    retention.value = 'true';
  } else {
    retention.value = 'false';
  }
}

function includeSharedCheckedBox() {
  const checkbox = document.getElementById('include-shared-toggle');
  const includeShared = document.getElementById('include-shared');
  if (checkbox.checked) {
    includeShared.value = 'true';
  } else {
    includeShared.value = 'false';
  }
}

function setCheckEvents() { // jshint ignore:line
  var retentionToggle = document.getElementById('retention-toggle');
  if (retentionToggle) {
    retentionToggle.addEventListener('click', retentionCheckedBox);
  }
  let includeSharedToggle = document.getElementById('include-shared-toggle');
  if (includeSharedToggle) {
    includeSharedToggle.addEventListener('click', includeSharedCheckedBox);
  }
}

function toggleOptionbox(toggleElement) { // jshint ignore:line
  let filterButton = document.getElementById(toggleElement);
  filterButton.style.display = (filterButton.style.display === "none") ? "block" : "none";
}

function toggleCheckbox(e, checkboxId) { // jshint ignore:line
  e.preventDefault();
  let checkbox = document.getElementById(checkboxId);
  checkbox.checked = !checkbox.checked;
}

function hideOptions(toggleElement) { // jshint ignore:line
  const options = ["sensitivity"];
  const toggleElem = document.getElementById(toggleElement);

  for (const option of options) {
    const checkbox = document.getElementById(option + "_checkbox");
    const filterElem = document.getElementById(option + "_filter");

    filterElem.hidden = !checkbox.checked;
  }

  toggleElem.style.display = "none";
}

function distributeAnyChecked() {
  return !!document.querySelector("input[name='distribute-to']:checked");
}

function updateDistributeButton() {
  var btn = document.getElementById("distribute-matches");
  if (!btn) {
    return;
  }
  btn.disabled = !distributeAnyChecked();
}

function updateActionButtons() {
  // Handle dialog buttons state when options are selected:
  var hasSelection = distributeAnyChecked();
  var releaseBtn = document.getElementById("distribute-matches");
  var clearBtn = document.getElementById("clear-distribute-selection");
  if (releaseBtn) {
    releaseBtn.disabled = !hasSelection;
  }
  if (clearBtn) {
    clearBtn.disabled = !hasSelection;
  }
}

function updateDistributeButton() {
  updateActionButtons();
}

function setDistributeSelectEvent() {
  var boxes = document.querySelectorAll("input[name='distribute-to']");
  if (!boxes.length) {
    return;
  }
  boxes.forEach(function (cb) {
    cb.addEventListener("change", updateDistributeButton);
  });
  updateActionButtons();
}

htmx.onLoad(function () {
  // When content is loaded with HTMX, reinstantiate dropdown and checkbox events:
  setDropdownEvent();
  setCheckEvents();
  setDistributeSelectEvent();
});

function wireDistributeDialog() {
  var dialog = document.getElementById("distribute-results-modal");
  var openBtn = document.getElementById("open-distribute-modal");

  if (openBtn && dialog && dialog.showModal) {
    openBtn.addEventListener("click", function () {
      dialog.showModal();
    });
  }

  // Close modal with any [data-close-dialog] button:
  document.querySelectorAll("[data-close-dialog]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      if (dialog && dialog.open) {
        dialog.close();
      }
    });
  });

  // Close modal when clicking outside the dialog box:
  if (dialog) {
    dialog.addEventListener("click", function (e) {
      if (e.target === dialog) {
        dialog.close();
      }
    });
  }

  // Make sure the "Distribute" button enable/disable still works with checkboxes:
  if (typeof setDistributeSelectEvent === "function") {
    setDistributeSelectEvent();
  }

  // Initialize dialog buttons when the dialog wires up:
  if (typeof updateActionButtons === "function") {
    updateActionButtons();
  }

  // Clear all selected checkboxes in the distribute dialog:
  var clearBtn = dialog && dialog.querySelector("#clear-distribute-selection");
  if (clearBtn) {
    clearBtn.addEventListener("click", function () {
      dialog.querySelectorAll("input[name='distribute-to']:checked")
        .forEach(function (cb) { cb.checked = false; });
      // Re-evaluate dialog buttons:
      updateActionButtons();
    });
  }
}

if (window.htmx && typeof htmx.onLoad === "function") {
  htmx.onLoad(() => {
    wireDistributeDialog();
  });
} else {
  document.addEventListener("DOMContentLoaded", () => {
    wireDistributeDialog();
  });
}
