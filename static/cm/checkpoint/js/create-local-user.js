$(document).ready(function () {
    $('#id_user_group').select2()
    document.querySelectorAll('input[name="action"]').forEach(radio => {
        radio.addEventListener('change', function () {
            document.getElementById('update-fields').style.display =
                (this.value === 'create') ? 'none' : 'block';
        });
    });
})