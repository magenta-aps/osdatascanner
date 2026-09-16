/* jshint -W098 */ //disable check is used ( called from html )

(function () {
  function closeSnackBar(el) {
    fadeAndRemoveSnackbar(el.parentNode.parentNode);
  }

  function fadeAndRemoveSnackbar(snackbar) {
    snackbar.classList.add("snackbar--fading-out");
    setTimeout(() => {
      snackbar.remove();
    }, 1000); // 1 second --> Has to match the fade out animation in _snackbars.scss
  }

  function recordSnackbarPositions() {
    const container = document.querySelector(".snackbar__container");
    const existing = container ? Array.from(container.children) : [];
    return new Map(existing.map((el) => [el, el.getBoundingClientRect()]));
  }

  function slideSnackbarsIntoPlace(beforeRects) {
    beforeRects.forEach((first, el) => {
      if (!el.isConnected) {
        return; // removed in the meantime, nothing to slide
      }
      const last = el.getBoundingClientRect();
      const deltaY = first.top - last.top;
      if (!deltaY) {
        return;
      }

      el.style.transition = "none";
      el.style.transform = `translateY(${deltaY}px)`;
      void el.offsetHeight; // force reflow so the browser registers the snap-back above

      // Keep the stylesheet's own opacity transition alongside this, in case this
      // sibling also happens to be mid fade-out (auto-close/manual close) right now.
      el.style.transition = "opacity 1s ease-out, transform 0.3s ease-out";
      el.style.transform = "";
      el.addEventListener(
        "transitionend",
        (evt) => {
          if (evt.propertyName === "transform") {
            el.style.transition = "";
          }
        },
        { once: true }
      );
    });
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
        <span class="snackbar__icon material-symbols">${icon}</span>
        <p class="snackbar__text">${message}</p>
        <button type="button" class="close-modal button button--modal-close snackbar__close-button" onclick="closeSnackBar(this)" title="Close">
          <span class="material-symbols">close</span>
        </button>
      </div>
    `;
    const beforeRects = recordSnackbarPositions();
    snackbarContainer.insertAdjacentElement("beforeend", snackbar);
    slideSnackbarsIntoPlace(beforeRects);
    autoCloseSnackBar();
  }

  function autoCloseSnackBar() {
    const snackbars = document.querySelectorAll(
      ".snackbar--auto_close:not([data-auto-close-wired])"
    );
    snackbars.forEach(function (snackbar) {
      snackbar.setAttribute("data-auto-close-wired", "true");
      let timer;
      let startTime;
      let remainingTime = 10000; // 10 seconds --> Has to match the timer animation in _snackbars.SCSS

      const startTimer = () => {
        clearTimeout(timer);
        startTime = Date.now();
        snackbar.style.setProperty("--animation-duration", `${remainingTime}ms`);
        timer = setTimeout(() => fadeAndRemoveSnackbar(snackbar), remainingTime);
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

  window.closeSnackBar = closeSnackBar;
  window.showSnackBar = showSnackBar;

  // Call this function when the page loads or after the snackbars are created
  autoCloseSnackBar();

  let pendingSnackbarRects = null;

  document.body.addEventListener("htmx:oobBeforeSwap", function (evt) {
    if (evt.detail.target && evt.detail.target.id === "snackbar") {
      pendingSnackbarRects = recordSnackbarPositions();
    }
  });

  document.body.addEventListener("htmx:oobAfterSwap", function (evt) {
    if (evt.detail.target && evt.detail.target.id === "snackbar") {
      if (pendingSnackbarRects) {
        slideSnackbarsIntoPlace(pendingSnackbarRects);
        pendingSnackbarRects = null;
      }
      autoCloseSnackBar();
    }
  });
})();
