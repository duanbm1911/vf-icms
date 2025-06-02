$(document).ready(function () {
  $('#list-created-rule-table').DataTable({
    'pageLength': 25
  });
  $('#list-process-rule-table').DataTable({
    'pageLength': 25
  });
  $('#list-success-rule-table').DataTable({
    'pageLength': 25
  });
  $('#list-failed-rule-table').DataTable({
    'pageLength': 25
  });
  $(document.body).on('click', '[data-toggle="modal"]', function () {
    var id = $(this).attr('id');
    var href = "/cm/fmc/access-rule/delete/" + id
    $('#delete-rule-from').attr('action', href)
  });
  $('#rule-list a').on('click', function (e) {
    e.preventDefault();
    $(this).tab('show');
  });
  $("ul.nav-tabs > li > a").on("shown.bs.tab", function (e) {
    var id = $(e.target).attr("href").substr(1);
    window.location.hash = id;
  });
  var hash = window.location.hash;
  $('#rule-list a[href="' + hash + '"]').tab('show');
});
