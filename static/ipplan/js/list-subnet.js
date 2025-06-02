$(document).ready(function() {
    $('#list-ip-subnet-table').DataTable({
      'pageLength': 50
    });
    $(document.body).on('click', '[data-toggle="modal"]', function() {
        var id = $(this).attr('id');
        var href = "/ipplan/delete-subnet/" + id
        $('#delete-subnet-from').attr('action', href)
      });
});
