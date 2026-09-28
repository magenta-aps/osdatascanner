/* jshint -W098 */
// NOTE: dropMenu() is called from the HTML, so silence "defined but never used".

// Show/hide the dropdown when the trigger button is clicked:
function dropMenu() {
  const menu = document.getElementById("userMenu");
  const isOpen = menu.classList.toggle("show");
  document.querySelector(".user-menu__trigger").setAttribute("aria-expanded", isOpen);
}

// Hide the dropdown, and optionally move focus back to the trigger:
function closeMenu(menu, returnFocus) {
  const trigger = document.querySelector(".user-menu__trigger");
  menu.classList.remove("show");
  trigger.setAttribute("aria-expanded", false);
  if (returnFocus) {
    trigger.focus();
  }
}

// Return the dropdown if it's open, otherwise `null` (it isn't rendered for logged-out users):
function getOpenMenu() {
  const menu = document.getElementById("userMenu");
  return menu && menu.classList.contains("show") ? menu : null;
}

// Hide the dropdown when the user clicks outside of it:
window.onclick = function (e) {
  const menu = getOpenMenu();
  if (menu && !e.target.closest(".user-menu__trigger, .user-menu__container")) {
    closeMenu(menu, false);
  }
};

// Hide the dropdown on `Escape` and move focus back to the trigger:
document.addEventListener("keydown", function (e) {
  const menu = getOpenMenu();
  if (menu && e.key === "Escape") {
    closeMenu(menu, true);
  }
});

// Hide the dropdown when keyboard focus moves outside the user-menu:
document.addEventListener("focusin", function (e) {
  const menu = getOpenMenu();
  if (menu && !e.target.closest(".user")) {
    closeMenu(menu, false);
  }
});

// NOTE: Not a part of the user-menu. This belongs to the header's navigation toggle.
// Toggle side navigation on small display sizes:
document.addEventListener('DOMContentLoaded', function () {
  document.getElementById("navigation-toggle").addEventListener("click", function (e) {
    const menu = document.getElementById("sidemenu") || document.getElementById('banner_menu');
    let toggle = e.target;
    let isHidden = !toggle.hasAttribute("aria-expanded") || toggle.getAttribute("aria-expanded") === "false";
    if (isHidden) {
      menu.style.display = "block";
      toggle.setAttribute("aria-expanded", "");
    } else {
      menu.style.display = "none";
      toggle.removeAttribute("aria-expanded");
    }
  });
});
