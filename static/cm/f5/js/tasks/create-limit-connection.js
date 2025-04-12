$(document).ready(function () {
    $('#id_vs_name').select2()
    $('#id_f5_device_ip').change(function() {
        let f5_device_ip = $('#id_f5_device_ip option:selected').text()
        $.ajax({
            type: 'GET',
            url: '/api/cm/f5/get/virtual-server?f5_device_ip=' + f5_device_ip,
            dataType:"json",
            success: function(response) {
                if (response.status == 'success') {
                    var list_ip_available = response.datalist
                    $('#id_vs_name').text('')
                    list_ip_available.forEach(vs_name => {
                        $('#id_vs_name').append($('<option>', { 
                            value: vs_name,
                            text : vs_name 
                        }))
                    });
                }
            }
        });
    });
});