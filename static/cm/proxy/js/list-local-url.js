$(document).ready(function() {
  $('#list-local-url-table').DataTable({
    'pageLength': 50
  });
  $(document.body).on('click', '[data-toggle="modal"]', function() {
      var id = $(this).attr('id');
      var href = "/cm/proxy/objects/delete-local-url/" + id
      $('#delete-local-url-form').attr('action', href)
    });
});
