$(document).ready(function() {
    $('#list-ip-location-table').DataTable({
      'pageLength': 50
    });
    $(document.body).on('click', '[data-toggle="modal"]', function() {
        var id = $(this).attr('id');
        var href = "/ipplan/delete-location/" + id
        $('#delete-location-from').attr('action', href)
      });
});
