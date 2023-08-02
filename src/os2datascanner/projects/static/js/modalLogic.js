function setModalEvents() {
  const textModalElements = document.querySelectorAll('[text-modal-element]');

  textModalElements.forEach(e => {
    const modalId = e.getAttribute("open-modal");
    const modal = document.querySelector(modalId);
    e.addEventListener("focusin", () => {
      e.value = "";
      modal.classList.remove('hidden');
    });
    e.addEventListener("focusout", () => {
      modal.classList.add('hidden');
    });
  });
}

function searchOrgUnitKeyUp() {
  const textField = document.querySelector('#org_units');
  const choices = document.querySelector('#org_units_list').querySelectorAll("li");
  textField.addEventListener("keyup", () => {
    const searchString = textField.value.toLowerCase();
    choices.forEach(choice => {
      const unitName = choice.textContent.toLowerCase();
      if (!unitName.includes(searchString)) {
        choice.style.display = "none";
      } else if (choice.style.display === "none") {
        choice.style.display = "";
      }
    });
  });
}

function inputOrgUnitsInSearchField() {
  const searchField = document.querySelector('#org_units');
  const overviewForm = document.querySelector('#leader_overview_form');
  const choices = document.querySelector('#org_units_list').querySelectorAll('li');
  choices.forEach(li => {
    li.addEventListener('click', () => {
      console.log(searchField);
      searchField.value = li.textContent;
      overviewForm.dispatchEvent(new Event('change'));
    });
  });
}

htmx.onLoad(content => {
  if (content.classList.contains('page') || content.classList.contains('content')) {
    inputOrgUnitsInSearchField();
    setModalEvents();
    searchOrgUnitKeyUp();
  }
});