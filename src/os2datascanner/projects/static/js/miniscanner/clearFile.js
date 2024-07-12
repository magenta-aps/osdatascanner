// Clears the selected file in the miniscanner file selection.
// Implemented for the user to be able to scan only text.

// jshint unused:false
function clearFile() {
    let inputField = document.getElementById("upload-file");
    inputField.value = "";
}
