$('#cleanup-accounts-modal').on($.modal.CLOSE, function () {
  let wrapp = document.querySelector('#cleanup-stale-accounts');
  wrapp.dispatchEvent(new Event('modal-closed'));
});

// Adds event listener to reload page to remove stale accounts button.
document.querySelector('#cleanup-stale-accounts').addEventListener('modal-closed', function () {
  location.reload();
});
