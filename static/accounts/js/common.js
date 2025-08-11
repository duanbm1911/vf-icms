$(document).ready(function () {
    $('select').selectize({
        sortField: 'text'
    });
    $('#table').DataTable({
        'pageLength': 50
    });
});
