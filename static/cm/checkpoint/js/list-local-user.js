$(document).ready(function () {
  $('#list-local-user-table').DataTable({
    'pageLength': 50
  });
  $(document.body).on('click', '[data-toggle="modal"]', function () {
    var id = $(this).attr('id');
    var href = "/cm/checkpoint/local-user/delete/" + id
    $('#delete-local-user-from').attr('action', href)
  });
});
