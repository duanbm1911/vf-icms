$(document).ready(function() {
  $('#list-user-table').DataTable({
    'pageLength': 50
  });
  $(document.body).on('click', '[data-toggle="modal"]', function() {
      var id = $(this).attr('id');
      var href = "/cm/checkpoint/user/delete/" + id
      $('#delete-user-form').attr('action', href)
    });
});
