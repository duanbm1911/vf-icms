$(document).ready(function() {
    $('#table').DataTable({
      'pageLength': 50
    });
    $(document.body).on('click', '[data-toggle="modal"]', function() {
        var id = $(this).attr('id');
        var href = "/cm/checkpoint/email-alert-template/delete/" + id
        $('#delete-form').attr('action', href)
      });
});
