/* ***** "Create Alias" Modal ***** */

/* jshint -W098 */ //disable check is used ( called from html )


// Change input validation criteria by selected alias type
function validateAliasType() {
  const aliasType = document.getElementById("id__alias_type").value;
  const valueField = document.getElementById("id__value");

  if (aliasType === "email") {
    valueField.setAttribute("type", "email");
  } else {
    // This might need to be updated if we ever decide to add more "specific" alias types
    valueField.setAttribute("type", "text");
  }
}

// Closing the modal
function closeModal() {
  const modalDialog = document.getElementById("add-alias-modal");
  if (modalDialog && typeof modalDialog.close === "function") {
    modalDialog.close();
  }
}
