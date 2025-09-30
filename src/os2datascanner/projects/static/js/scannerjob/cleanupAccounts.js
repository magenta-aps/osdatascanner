$('#cleanup-accounts-modal').on($.modal.CLOSE, function () {
  let wrapp = document.querySelector('#cleanup-stale-accounts');
  wrapp.dispatchEvent(new Event('modal-closed'));
});

// Adds event listener and event to reload stale accounts button.
document.querySelector('#cleanup-stale-accounts').addEventListener('modal-closed', function (e) {
  e.target.dispatchEvent(new Event("update-stale-accounts"));
});
