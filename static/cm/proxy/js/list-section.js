$(document).ready(function() {
  $('#list-section-table').DataTable({
    'pageLength': 50
  });
  $(document.body).on('click', '[data-toggle="modal"]', function() {
      var id = $(this).attr('id');
      var href = "/cm/proxy/objects/delete-section/" + id
      $('#delete-section-form').attr('action', href)
    });
});
