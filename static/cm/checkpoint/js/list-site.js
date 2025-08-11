$(document).ready(function() {
    $('#list-site-table').DataTable({
      'pageLength': 50
    });
    $(document.body).on('click', '[data-toggle="modal"]', function() {
        var id = $(this).attr('id');
        var href = "/cm/checkpoint/site/delete/" + id
        $('#delete-site-from').attr('action', href)
      });
});
