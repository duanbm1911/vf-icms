$(document).ready(function () {
  $('#list-domain-table').DataTable({
    'pageLength': 50
  });
  $(document.body).on('click', '[data-toggle="modal"]', function () {
    var id = $(this).attr('id');
    var href = "/cm/fmc/domain/delete/" + id
    $('#delete-site-from').attr('action', href)
  });
});
