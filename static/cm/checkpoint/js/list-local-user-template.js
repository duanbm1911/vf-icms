$(document).ready(function() {
    $('#list-local-user-template-table').DataTable({
      'pageLength': 50
    });
    $(document.body).on('click', '[data-toggle="modal"]', function() {
        var id = $(this).attr('id');
        var href = "/cm/checkpoint/local-user-template/delete/" + id
        $('#delete-local-user-template-from').attr('action', href)
      });
});
