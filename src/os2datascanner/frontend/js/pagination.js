// Jump to specific page
document.addEventListener("click", function(e) {
  if (e.target.id === "form-button") {
    e.preventDefault();
    var page_number = document.querySelector('input[type="number"]').value;

    if ('URLSearchParams' in window) {
        var searchParams = new URLSearchParams(window.location.search);
        searchParams.set("page", page_number);
        window.location.search = searchParams.toString();
    }
  }
});
