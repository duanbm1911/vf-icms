$(document).ready(function() {
    $('#list-ip-subnet-group-table').DataTable({
      'pageLength': 50
    });
    $(document.body).on('click', '[data-toggle="modal"]', function() {
        var id = $(this).attr('id');
        var href = "/ipplan/delete-subnet-group/" + id
        $('#delete-subnet-group-from').attr('action', href)
      });
});
