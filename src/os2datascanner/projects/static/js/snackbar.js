document.body.addEventListener("reload-htmx", function (response) {
  const details = response.detail;
  const pks = document.querySelector("#pks_input");
  const action = document.querySelector("#action_input");
  if ("pks" in details) {
    pks.value = details.pks;
  } else {
    pks.value = null;
  }
  if ("action" in details) {
    action.value = details.action;
  } else {
    action.value = null;
  }
});