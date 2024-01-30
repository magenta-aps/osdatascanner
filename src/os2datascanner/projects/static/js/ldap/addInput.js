// add input field for user class object
let btnUserClass = document.querySelector("#btnUserClass");
let counter = 1;
let div = document.getElementById("userObjClass");
let taglist = [];
let firstInput = document.querySelector("#userClass");
let inputValues = document.querySelectorAll(".user-class-input");
let hiddenInput = document.getElementsByName("user_obj_classes")[0];

// add new input field
let addInput = function () {
  counter += 1;

  // flex container for input field + remove button
  let inputButtonContainer = document.createElement("div");
  inputButtonContainer.id = "container" + counter;
  inputButtonContainer.className = "flex";

  // input field
  let input = document.createElement("input");
  input.id = "userClass" + counter;
  input.type = "text";
  input.name = "userClass" + counter;
  input.className = "user-class-input";

  // place input + button inside flex container
  inputButtonContainer.appendChild(input);
  inputButtonContainer.appendChild(
    removeUserClass(input, inputButtonContainer)
  );
  addUserClassInput(input);

  div.appendChild(inputButtonContainer);
};
btnUserClass.addEventListener(
  "click",
  function () {
    addInput();
  }.bind(this)
);

// remove button
function removeUserClass(element, parent) {
  let btnRemove = document.createElement("button");
  btnRemove.addEventListener("click", function () {
    parent.parentNode.removeChild(parent);
    updateTagList();
  });
  btnRemove.id = "removeUserClass" + counter;
  btnRemove.type = "button";
  btnRemove.name = "removeUserClass" + counter;
  btnRemove.textContent = "Fjern";
  btnRemove.className += "button button--transparent-button";
  return btnRemove;
}

// update tag list on change
function addUserClassInput(element) {
    element.addEventListener('change', updateTagList);
}
function updateTagList() {
    inputValues = document.querySelectorAll('.user-class-input');
    taglist = [];
    for (let i = 0; i < inputValues.length; i += 1) {  
        taglist.push(inputValues[i].value);
    }
    hiddenInput.value = taglist.join(', ');
}

function saveInputs() {
    if (hiddenInput.value) {
      // dont show input field in ui (this input field contains all input values)
      hiddenInput.style.display = "none";
      inputValues[0].value = hiddenInput.value.split(",");
   } else {
      hiddenInput.style.display = "none";
   }
}

addUserClassInput(firstInput);
saveInputs();
