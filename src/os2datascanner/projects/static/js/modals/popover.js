// Add popover listeners
function addPopoverListeners() {
  const popoverTriggers = document.querySelectorAll(".popoverTrigger");
  popoverTriggers.forEach(function (trigger) {
    trigger.addEventListener("mouseenter", showPopover);
    trigger.addEventListener("mouseleave", hidePopover);
  });
}

// Show a popover based on an event and its target
function showPopover(event) {
  let wrapper = event.target;
  let popoverId = wrapper.getAttribute("data-popover-id");
  if (popoverId) {
    let popover = document.getElementById(popoverId);
    if (popover) {
      popover.style.display = "block";
    }
  }
}

// Hide the popover
function hidePopover(event) {
  let wrapper = event.target;
  let popoverId = wrapper.getAttribute("data-popover-id");
  if (popoverId) {
    let popover = document.getElementById(popoverId);
    if (popover) {
      popover.style.display = "none";
    }
  }
}

// Initialize popover functionality
htmx.onLoad(function () {
  addPopoverListeners();
});
