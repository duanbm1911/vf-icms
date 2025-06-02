$(document).ready(function() {
  $('#list-process-table').DataTable({
    'pageLength': 50
  });
  $('#list-result-table').DataTable({
    'pageLength': 50
  });
  $(document.body).on('click', '[data-toggle="modal"]', function() {
      var id = $(this).attr('id');
      var name = $(this).attr('name')
      var href = "/cm/f5/tasks/delete/" + name + "/" + id
      $('#delete-task-form').attr('action', href)
    });
});
