// jshint unused:false
function checkTextSize(inputElement, maxSize=2000) {
    const textValue = inputElement.value
    const errorText = document.getElementById("text-upload-error-response").innerText;

    if (textValue.length > maxSize) {
        inputElement.setCustomValidity(errorText);
    } else {
        inputElement.setCustomValidity("");
    }
}