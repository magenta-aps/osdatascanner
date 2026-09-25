/* jshint -W098 */ //disable check is used ( called from html )
/* When the user clicks on the button,
toggle between hiding and showing the dropdown content */
function dropMenu() {
  const menu = document.getElementById("userMenu");
  const isOpen = menu.classList.toggle("show");
  document.querySelector(".user-menu__trigger").setAttribute("aria-expanded", isOpen);
}

// Close the dropdown if the user clicks outside of it
window.onclick = function (e) {
  if (!e.target.closest(".user-menu__trigger, .user-menu__container")) {
    const menu = document.getElementById("userMenu");
    if (menu.classList.contains("show")) {
      menu.classList.remove("show");
      document.querySelector(".user-menu__trigger").setAttribute("aria-expanded", false);
    }
  }
};

// Toggle side navigation on small display sizes
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
