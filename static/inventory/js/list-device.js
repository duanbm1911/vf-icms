$(document).ready(function () {
  $('#id_device_os').selectize({ sortField: 'text' });
  $('#id_device_tag').selectize({ sortField: 'text' });
  $('#id_device_vendor').selectize({ sortField: 'text' });
  $('#id_device_category').selectize({ sortField: 'text' });
  $('#id_device_type').selectize({ sortField: 'text' });
  $('#id_device_branch').selectize({ sortField: 'text' });
  $(document.body).on('click', '[data-toggle="modal"]', function () {
    var id = $(this).attr('id');
    var href = "/inventory/device/delete/" + id;
    $('#delete-form').attr('action', href);
  });
});
