$(document).ready(function () {
    $('#id_subnet').select2()
    $('#id_ip').select2()
    $('#id_subnet').change(function() {
        let subnet = $('#id_subnet option:selected').text()
        $.ajax({
            type: 'GET',
            url: '/api/ipplan/get-list-ip-available?subnet=' + subnet,
            dataType:"json",
            success: function(response) {
                if (response.status == 'success') {
                    var list_ip_available = response.data
                    $('#id_ip').text('')
                    list_ip_available.forEach(ip => {
                        $('#id_ip').append($('<option>', { 
                            value: ip,
                            text : ip 
                        }))
                    });
                    $('#ip-available').text('')
                    $('#ip-available').html('<strong style="color:green">Available: ' + list_ip_available.length + ' IP</strong>')
                }
                else {
                    $('#ip-available').text('')
                    $('#ip-available').html('<strong style="color:red">' + response.error + '</strong>')
                }
            },
        });
    });
    $('#request-ip-form').on('submit', function() {
        let list_ip = $('#id_ip').val()
        // $('#id_ip').text(list_ip)
    })
});