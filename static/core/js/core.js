jQuery(document).ready(function ($) {
  $("#loader-overlay").hide();
  $("#main-content").show();
  setTimeout(function () {
    $(".alert").fadeOut("slow");
  }, 5000);
  $('li.dropdown-submenu a[data-toggle="dropdown"]').on('click', function (event) {
    event.preventDefault();
    event.stopPropagation();
    $('li.dropdown-submenu').not($(this).parent()).removeClass('open');
    $(this).parent().toggleClass('open');
  });
});
