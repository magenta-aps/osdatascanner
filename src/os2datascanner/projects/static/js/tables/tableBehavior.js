// Remove rounds corners of table when stuck on top of screen.
function handleTableCorners() {
  const stickyElm = document.querySelector(".table-topbar");

  const observer = new IntersectionObserver(
    ([e]) => e.target.classList.toggle("stuck", e.intersectionRatio < 1),
    { rootMargin: "-1px 0px 0px 0px", threshold: [1] }
  );

  if (stickyElm) {
    observer.observe(stickyElm);
  }
}

// Handle checkboxes
function handleChecked() {
  let numChecked = $("input[name='table-checkbox']:checked").length;
  $(".selected-cb .num-selected").text(numChecked);
  $(".table-checkbox__action").prop("disabled", !Boolean(numChecked));

  $("input[name='table-checkbox']:not(:checked)")
    .closest("tr")
    .removeClass("highlighted");
  $("input[name='table-checkbox']:checked")
    .closest("tr")
    .addClass("highlighted");
}

// attach click handler to document to be prepared for the scenario
// where we dynamically add more rows
document.addEventListener("click", function (e) {
  let row;
  let targ = e.target;

  if (hasClass(targ, "matches-expand")) {
    // toggle the matches of a single row
    row = closestElement(targ, "tr[data-type]");
    toggleMatchesList([row], targ);
  }

  if (hasClass(targ, "matches-expand-all")) {
    // toggle the matches of all rows
    const rows = document.querySelectorAll("tr[data-type]");
    toggleMatchesList(rows, targ);

    // store the user's preference in window.localStorage
    const preferenceExpand = hasClass(targ, "up") ? "expanded" : "collapsed";
    setStorage("os2ds-prefers-expanded-results", preferenceExpand);
  }

  if (hasClass(targ, "toggle-next-row")) {
    // toggle the matches of a single row
    row = closestElement(targ, "tr");
    if (row) {
      toggleMatchesList([row], targ);
    }
  }

  if (hasClass(targ, "probability-toggle")) {
    const isPressed = targ.getAttribute("aria-pressed") === "true";
    if (isPressed) {
      targ.setAttribute("aria-pressed", "false");
    } else {
      targ.setAttribute("aria-pressed", "true");
    }

    Array.prototype.forEach.call(
      document.querySelectorAll(".matches-list__column--probability"),
      function (col) {
        if (isPressed) {
          col.setAttribute("hidden", "");
        } else {
          col.removeAttribute("hidden");
        }
      }
    );

    // store the user's preference in window.localStorage
    const preferenceProbability = isPressed ? "hide" : "show";
    setStorage("os2ds-prefers-probability", preferenceProbability);
  }

  if (hasClass(targ, "order-by")) {
    document.getElementById("order").value = targ.value;
    document.getElementById("order_by").value = targ.name;
  }

  // ***** Toggle for <td>'s with a "show more" button *****
  const btn = e.target.closest(".show-more");
  if (!btn) {
    return;
  }

  const overflow = btn.parentElement;
  const expanded = overflow.classList.toggle("full-path");
  btn.setAttribute("aria-expanded", expanded ? "true" : "false");
  btn.textContent = expanded
    ? btn.dataset.labelExpanded
    : btn.dataset.labelCollapsed;
});

// function to use localStorage
function setStorage(item, value) {
  try {
    window.localStorage.setItem(item, value);
  } catch (e) {
    console.error(
      "Could not save " + item + " with value " + value + " to localStorage",
      e
    );
  }
}

// IE11 way of doing Element.closest
function closestElement(elm, selector) {
  let parent = elm;
  while (parent) {
    if (parent.matches(selector)) {
      break;
    }
    parent = parent.parentElement;
  }
  return parent;
}

function toggleMatchesList(objectRows, toggleButton) {
  toggleClass(toggleButton, "up");
  const buttonOpen = hasClass(toggleButton, "up");

  Array.prototype.forEach.call(objectRows, function (row) {
    var matchesList = row.nextElementSibling;

    // show/hide the matches. We can't just toggle their state as
    // we may have clicked the matches-expand-all button, so we need to read
    // the state from the button that was clicked.
    // toggleButton may be the button that belongs to the row we're iterating
    // or it may be the matches-expand-all button. If the latter is the case,
    // we also need to toggle the button that belongs to the row.
    matchesList.hidden = !buttonOpen;
    rowButton = row.querySelector(".matches-expand");
    if (buttonOpen) {
      addClass(row, "up");
      if (rowButton !== toggleButton) {
        addClass(rowButton, "up");
      }
    } else {
      removeClass(row, "up");
      if (rowButton !== toggleButton) {
        removeClass(rowButton, "up");
      }
    }
  });
}

// IE11 way of doing Element.classList.add and Element.classList.remove
function toggleClass(elm, className) {
  if (!hasClass(elm, className)) {
    addClass(elm, className);
  } else {
    removeClass(elm, className);
  }
}

function addClass(elm, className) {
  if (!hasClass(elm, className)) {
    elm.className = (elm.className + " " + className).trim();
  }
}

function removeClass(elm, className) {
  elm.className = elm.className.replace(className, "").trim();
}

// IE11 way of doing elm.classList.contains
function hasClass(elm, className) {
  classList = [];
  if (typeof elm.className === "string") {
    classList = elm.className ? elm.className.split(" ") : [];
  } else {
    classList = Array.from(elm.classList);
  }
  return classList.indexOf(className) > -1;
}

function showTooltip(event) {
  let wrapper = event.target.closest(".tooltip");
  if (!wrapper) {
    return;
  }

  const tooltipElm = wrapper.querySelector("[data-tooltip-text]");
  if (!tooltipElm) {
    return;
  }

  const textWidth = tooltipElm.offsetWidth;
  const wrapperStyle = getComputedStyle(wrapper);
  const wrapperWidth =
    wrapper.offsetWidth -
    parseFloat(wrapperStyle.paddingLeft) -
    parseFloat(wrapperStyle.paddingRight);

  // If a tooltip already exists, don't create another one
  if (wrapper.querySelector("[data-tooltip]")) {
    return;
  }

  if (textWidth > wrapperWidth) {
    addClass(wrapper, "cursor-help");
    let tip = document.createElement("div");
    const rect = wrapper.getBoundingClientRect();
    const x = Math.round(event.pageX - rect.left - window.scrollX);
    const y = Math.round(event.pageY - rect.top - window.scrollY);
    tip.innerText = tooltipElm.innerText;
    tip.setAttribute("data-tooltip", "");
    tip.setAttribute("style", "top:" + y + "px;left:" + x + "px;");
    wrapper.appendChild(tip);
  }
}

function hideTooltip(event) {
  const wrapper = event.target.closest(".tooltip");
  if (!wrapper) {
    return;
  }

  const tooltip = wrapper.querySelector("[data-tooltip]");
  if (tooltip) {
    tooltip.remove();
  }
}

// Function to toggle visibility of "show-more" buttons based on screen size
function toggleShowMoreButtons() {
  const pathContainers = document.querySelectorAll(".overflow-ellipsis");
  const isLargeScreen = window.matchMedia("(min-width: 1200px)").matches;

  pathContainers.forEach((pathContainer) => {
    const moreBtn = pathContainer.querySelector(".show-more");
    if (moreBtn) {
      // Check if the text is overflowing
      const isOverflowing =
        pathContainer.scrollWidth > pathContainer.clientWidth;

      // Show the button only if it's a large screen and the content is overflowing
      moreBtn.style.display = isLargeScreen && isOverflowing ? "block" : "none";
    }
  });
}

function prepareTable() {
  // if user prefers to have all rows expanded, do that.
  const prefersExpanded = window.localStorage.getItem(
    "os2ds-prefers-expanded-results"
  );
  if (prefersExpanded && prefersExpanded === "expanded") {
    document.querySelector(".matches-expand-all").click();
  }

  // Uncheck checkboxes on load (unless they have the "keep-value" class).
  $("input[name='table-checkbox']:not('.keep-value')").prop("checked", false);
  $("#select-all").prop("checked", false);
  $(".table-checkbox__action").prop("disabled", true);

  // if user prefers to see probability, do that.
  const prefersProbability = window.localStorage.getItem(
    "os2ds-prefers-probability"
  );
  if (prefersProbability && prefersProbability === "show") {
    document.querySelector(".probability-toggle").click();
  }

  handleTableCorners();
}

// Delegated Event Listeners for dynamically loaded tooltips
document.addEventListener("mouseover", function (event) {
  const tooltip = event.target.closest(".tooltip");
  if (tooltip) {
    showTooltip(event);
  }
});

document.addEventListener("mouseout", function (event) {
  const wrapper = event.target.closest(".tooltip");
  if (wrapper && !wrapper.contains(event.relatedTarget)) {
    hideTooltip(event);
  }
});

document.addEventListener("DOMContentLoaded", function () {
  prepareTable();

  htmx.onLoad(function (content) {
    if (
      hasClass(content, "page") ||
      hasClass(content, "datatable-wrapper") ||
      hasClass(content, "datatablex__wrapper") ||
      hasClass(content, "content")
    ) {
      prepareTable();

      // Listen for click on toggle checkbox
      $("#select-all").change(function () {
        $("input[name='table-checkbox']").prop(
          "checked",
          $(this).prop("checked")
        );
        handleChecked();
      });

      // Iterate each checkbox
      $("input[name='table-checkbox']").change(handleChecked);

      // Copy Path function
      if (typeof ClipboardJS !== "undefined") {
        new ClipboardJS(document.querySelectorAll("[data-clipboard-text]"));
      }

      expandOverflowButton();
    }
  });

  function isContentOverflowing(element) {
    return element.scrollWidth > element.clientWidth;
  }

  function expandOverflowButton() {
    const pathContainers = document.querySelectorAll(".overflow-ellipsis");
    pathContainers.forEach((pathContainer) => {
      const moreBtn = pathContainer.querySelector(".show-more");

      if (moreBtn && isContentOverflowing(pathContainer)) {
        moreBtn.style.display = "block";
      }
    });
  }

  // Add call to toggle visibility of "show-more" buttons
  toggleShowMoreButtons();

  // Add resize listener to adjust visibility dynamically
  window.addEventListener("resize", toggleShowMoreButtons);
});
