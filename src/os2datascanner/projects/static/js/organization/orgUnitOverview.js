
function setAddButtons(buttons) {
  buttons.forEach(element => {
    element.addEventListener("click", function () {
      let selectField = element.parentNode.querySelector(".select_options");
      element.style.display = "none";
      selectField.hidden = false;
    });
  });
}

htmx.onLoad(function (content) {
  let addButtons = content.querySelectorAll(".add_button");
  setAddButtons(addButtons);

  revealHighlighted(content);
});