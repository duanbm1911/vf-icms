$(document).ready(function() {
  $('#list-device-table').DataTable({
    'pageLength': 50
  });
  $(document.body).on('click', '[data-toggle="modal"]', function() {
      var id = $(this).attr('id');
      var href = "/cm/f5/device/delete/" + id
      $('#delete-device-form').attr('action', href)
    });
});
