/***** ClearableFileInput UX improvements *****/
// Problem:   Django's native ClearableFileInput template includes a “delete on next save” checkbox that can confuse users.
// Solution:  Replace the server-rendered display with a custom UI, while keeping Django’s original inputs and checkbox
//            fully wired up under the hood.

// Helpers:
const qs = (sel, root) => (root || document).querySelector(sel);
const fieldOf = (el) => el.closest('[data-widget="file"]');
const emptyLabel = (f) => {
  if (f && f.dataset && typeof f.dataset.emptyLabel !== "undefined") {
    return f.dataset.emptyLabel;
  }
  return "No file chosen";
};

// Clone the "new upload" template and insert the filename:
function makeNewDisplay(fileName) {
  const tpl = qs('template[data-template="uploaded-new"]');
  const node = tpl.content.firstElementChild.cloneNode(true);
  const nameEl = qs('[data-role="filename"]', node);
  if (nameEl) {
    nameEl.textContent = fileName;
  }
  return node;
}

// Open the native file picker for this widget:
document.addEventListener("click", (e) => {
  const btn = e.target.closest('[data-action="upload-file"]');
  if (!btn) {
    return;
  }
  const field = fieldOf(btn);
  const input = qs('input[type="file"][data-role="form-input"]', field);
  if (input) {
    input.click();
  }
});

// When a new file is chosen:
document.addEventListener("change", (e) => {
  const input = e.target.closest('input[type="file"][data-role="form-input"]');
  if (!input) {
    return;
  }

  const field = fieldOf(input);
  const content = qs('[data-role="content"]', field);
  const display = qs('[data-role="display"]', content);
  const clear = qs('[data-role="clear-existing"]', content);

  // Snapshot the current display so we can restore it if the user cancels:
  if (display && !content.__prevDisplay) {
    content.__prevDisplay = display.cloneNode(true);
  }

  // Uncheck the delete-on-next-save checkbox:
  if (clear) {
    clear.checked = false;
  }

  // Swap the display to show the new filename:
  if (input.files && input.files.length > 0) {
    const node = makeNewDisplay(input.files[0].name);
    display.replaceWith(node);
  }
});

// Remove the existing (previously saved) file:
document.addEventListener("click", (e) => {
  const btn = e.target.closest('[data-action="remove-existing"]');
  if (!btn) {
    return;
  }

  const field = fieldOf(btn);
  const content = qs('[data-role="content"]', field);
  const display = qs('[data-role="display"]', content);
  const input = qs('input[type="file"][data-role="form-input"]', field);
  const clear = qs('[data-role="clear-existing"]', content);

  const hasNew = !!(input && input.files && input.files.length > 0);

  // If a replacement exists, leave the delete checkbox unchecked and keep the new display:
  if (clear) {
    clear.checked = !hasNew;
    content.dataset.priorClearIntent = clear.checked ? "1" : "0";
  }

  // If no replacement exists, check the delete checkbox and show the placeholder:
  if (!hasNew && display) {
    display.className = "uploaded-file uploaded-file--empty";
    display.innerHTML =
      '<span class="uploaded-file__placeholder">' +
      emptyLabel(field) +
      "</span>";
  }
});

// Remove the newly selected file:
document.addEventListener("click", (e) => {
  const btn = e.target.closest('[data-action="remove-new"]');
  if (!btn) {
    return;
  }

  const field = fieldOf(btn);
  const content = qs('[data-role="content"]', field);
  const display = qs('[data-role="display"]', content);
  const input = qs('input[type="file"][data-role="form-input"]', field);
  const clear = qs('[data-role="clear-existing"]', content);

  // Clear the <input type="file">:
  if (input) {
    input.value = "";
  }

  // Restore the prior delete intent (if set when removing the existing file):
  const wantedClear = !!(
    content &&
    content.dataset &&
    content.dataset.priorClearIntent === "1"
  );
  if (clear) {
    clear.checked = wantedClear;
  }

  // Restore the original server-rendered display if snapshotted; otherwise show the placeholder:
  if (content && content.__prevDisplay) {
    display.replaceWith(content.__prevDisplay);
    content.__prevDisplay = null;
  } else if (display) {
    display.className = "uploaded-file uploaded-file--empty";
    display.innerHTML =
      '<span class="uploaded-file__placeholder">' +
      emptyLabel(field) +
      "</span>";
  }
});
