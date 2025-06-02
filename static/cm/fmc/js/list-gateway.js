$(document).ready(function () {
  $('#list-gateway-table').DataTable({
    'pageLength': 50
  });
  $(document.body).on('click', '[data-toggle="modal"]', function () {
    var id = $(this).attr('id');
    var href = "/cm/fmc/gateway/delete/" + id
    $('#delete-gateway-from').attr('action', href)
  });
});
