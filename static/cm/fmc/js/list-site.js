$(document).ready(function () {
  $('#list-site-table').DataTable({
    'pageLength': 50
  });
  $(document.body).on('click', '[data-toggle="modal"]', function () {
    var id = $(this).attr('id');
    var href = "/cm/fmc/site/delete/" + id
    $('#delete-site-from').attr('action', href)
  });
});
