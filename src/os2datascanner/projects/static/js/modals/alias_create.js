/* ***** "Create Alias" Modal ***** */

/* jshint -W098 */ //disable check is used ( called from html )


// Closing the modal
function closeModal() {
  const modalDialog = document.getElementById("add-alias-modal");
  if (modalDialog && typeof modalDialog.close === "function") {
    modalDialog.close();
  }
}
