/* jshint -W098 */ //disable check is used ( called from html )

// Old snackbar
function closeOldSnackBar(el) {
  el.parentNode.remove();
}

// New snackbar
function closeNewSnackBar(el) {
  el.parentNode.parentNode.remove();
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
