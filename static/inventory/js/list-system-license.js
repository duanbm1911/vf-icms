$(document).ready(function () {
  $(document.body).on('click', '[data-toggle="modal"]', function () {
    var id = $(this).attr('id');
    var href = "/inventory/license/delete/" + id
    $('#delete-form').attr('action', href)
  });
});
