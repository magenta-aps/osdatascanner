/* jshint -W098 */ //disable check is used ( called from html )

// Old snackbar
function closeOldSnackBar(el) {
  el.parentNode.remove();
}

// New snackbar
function closeNewSnackBar(el) {
  el.parentNode.parentNode.remove();
}

function showSnackBar(message, type) {
  let snackbarContainer = document.querySelector(".snackbar__container");
  if (!snackbarContainer) {
    snackbarContainer = document.createElement("div");
    snackbarContainer.id = "snackbar";
    snackbarContainer.className = "snackbar__container";
    document.body.appendChild(snackbarContainer);
  }

  const snackbar = document.createElement("div");
  const icon =
    type === "success"
      ? "check_circle"
      : type === "warning"
      ? "warning"
      : type === "error"
      ? "error"
      : "info";

  snackbar.classList.add("snackbar", type, "snackbar--auto_close");
  snackbar.innerHTML = `
    <div class="snackbar__content">
      <span class="snackbar__icon material-icons">${icon}</span>
      <p class="snackbar__text">${message}</p>
      <button type="button" class="close-modal button button--modal-close snackbar__close-button" onclick="closeNewSnackBar(this)" title="Close">
        <span class="material-icons">close</span>
      </button>
    </div>
  `;
  // Use afterbegin to have new snackbars appear on top
  snackbarContainer.insertAdjacentElement("afterbegin", snackbar);
  autoCloseSnackBar();
}

function autoCloseSnackBar() {
  const snackbars = document.querySelectorAll(".snackbar--auto_close");
  snackbars.forEach(function (snackbar) {
    let timer;
    let startTime;
    let remainingTime = 8000; // 8 seconds --> Has to match the timer animation in _snackbars.SCSS

    const closeSnackbar = () => {
      snackbar.classList.add("snackbar--fading-out");
      setTimeout(() => {
        snackbar.remove();
      }, 1000); // 1 second --> Has to match the fade out animation in _snackbars.SCSS
    };

    const startTimer = () => {
      clearTimeout(timer);
      startTime = Date.now();
      snackbar.style.setProperty("--animation-duration", `${remainingTime}ms`);
      timer = setTimeout(closeSnackbar, remainingTime);
      snackbar.style.animationPlayState = "running"; // Resume the animation
    };

    const pauseTimer = () => {
      clearTimeout(timer);
      remainingTime -= Date.now() - startTime; // Update remaining time
      snackbar.style.animationPlayState = "paused"; // Pause the animation
    };

    snackbar.addEventListener("mouseover", pauseTimer);
    snackbar.addEventListener("mouseout", startTimer);

    // Start the initial timer
    startTimer();
  });
}

// Call this function when the page loads or after the snackbars are created
autoCloseSnackBar();
