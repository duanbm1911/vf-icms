$(document).ready(function () {
    $(document.body).on('click', '[data-toggle="modal"]', function () {
        var id = $(this).attr('id');
        var href = "/inventory/device/rack-layout/delete/" + id
        $('#delete-form').attr('action', href)
    });
});
