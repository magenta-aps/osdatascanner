// jshint unused:false
function checkFileSize(inputElement, maxSizeStr) {
    const files = inputElement.files;
    const maxSize = +(maxSizeStr.replaceAll('.', ''));
    const errorText = document.getElementById("file-upload-error-response").innerText;
    const runButton = document.getElementById("run-miniscan-btn");

    if (files.length > 0 && files[0].size > maxSize) {
        inputElement.setCustomValidity(errorText);
        runButton.disabled = true;
    } else {
        inputElement.setCustomValidity("");
        runButton.disabled = false;
    }
}
