$(document).ready(function() {
    $('#list-ip-region-table').DataTable({
      'pageLength': 50
    });
    $(document.body).on('click', '[data-toggle="modal"]', function() {
        var id = $(this).attr('id');
        var href = "/ipplan/delete-region/" + id
        $('#delete-region-from').attr('action', href)
      });
});
