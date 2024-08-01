$(document).ready(function() {
    $('.update-users-button').on('click', function() {
        var button = $(this);
        button.prop('disabled', true); // Блокируем кнопку
    
        $('#loading-indicator').show();
    
        $.ajax({
            url: '/users/update-users-data/',
            method: 'GET',
            dataType: 'json',
            success: function(response, textStatus, xhr) {
                $('#loading-indicator').hide();
                button.prop('disabled', false); // Разблокируем кнопку

                $('#success-message').text('Данные успешно обновлены!').show();
                $('#error-message').hide();
                setTimeout(function() {
                    location.reload(); // Перезагрузка страницы
                }, 1500); // Задержка 2 секунды
            },
            error: function(xhr) {
                $('#loading-indicator').hide();
                button.prop('disabled', false); // Разблокируем кнопку
    
                // Проверяем, был ли ответ JSON и содержит ли он ошибку
                try {
                    var jsonResponse = JSON.parse(xhr.responseText);
                    if (jsonResponse.error) {
                        $('#error-message').text('Ошибка: ' + jsonResponse.error + ' (Статус код: ' + xhr.status + ')').show();
                    } else {
                        $('#error-message').text('Неизвестная ошибка. (Статус код: ' + xhr.status + ')').show();
                    }
                } catch (e) {
                    $('#error-message').text('Произошла ошибка при запросе. (Статус код: ' + xhr.status + ')').show();
                }
    
                $('#success-message').hide();
            }
        });
    });

    $('.edit-rdlogin-btn').click(function() {
        var row = $(this).closest('tr');
        var rdloginSelect = row.find('select[name="rdlogin"]');

        rdloginSelect.select2({
                width: '50%',
                dropdownAutoWidth: true
            });

        $.getJSON('/users/get-rdlogins/', function(rdlogins) {
            rdloginSelect.empty();
            $.each(rdlogins, function(index, rdlogin) {
                rdloginSelect.append($('<option>', {
                    value: rdlogin.id,
                    text: rdlogin.login
                }));
            });
            rdloginSelect.trigger('change');
            rdloginSelect.select2('open');
        });

        $(this).hide();
        row.find('.delete-rdlogin-btn').hide();
        row.find('.save-rdlogin-btn').show();
        row.find('.cancel-rdlogin-btn').show();
    });

    $('.edit-vpn-btn').click(function() {
        var row = $(this).closest('tr');
        var vpnSelect = row.find('select[name="vpn"]');

        vpnSelect.select2({
                width: '50%',
                dropdownAutoWidth: true
            });

        $.getJSON('/users/get-vpns/', function(vpns) {
            vpnSelect.empty();
            $.each(vpns, function(index, vpn) {
                vpnSelect.append($('<option>', {
                    value: vpn.id,
                    text: vpn.login
                }));
            });
            vpnSelect.trigger('change');
            vpnSelect.select2('open');
        });

        $(this).hide();
        row.find('.delete-vpn-btn').hide();
        row.find('.save-vpn-btn').show();
        row.find('.cancel-vpn-btn').show();
    });

    $('.cancel-rdlogin-btn').click(function() {
        var row = $(this).closest('tr');
        row.find('.rdlogin-value').show();
        row.find('select[name="rdlogin"]').select2('destroy').hide();
        row.find('.edit-rdlogin-btn').show();
        row.find('.delete-rdlogin-btn').show();
        row.find('.save-rdlogin-btn').hide();
        row.find('.cancel-rdlogin-btn').hide();
    });

    $('.cancel-vpn-btn').click(function() {
        var row = $(this).closest('tr');
        row.find('.vpn-value').show();
        row.find('select[name="vpn"]').select2('destroy').hide();
        row.find('.edit-vpn-btn').show();
        row.find('.delete-vpn-btn').show();
        row.find('.save-vpn-btn').hide();
        row.find('.cancel-vpn-btn').hide();
    });

    $('.save-rdlogin-btn').click(function() {
        var row = $(this).closest('tr');
        var userId = row.data('user-id');
        var rdloginId = row.find('select[name="rdlogin"]').val();

        if (rdloginId) {
            $.ajax({
                url: edit_user_url,
                method: 'POST',
                data: {
                    'ad_user_id': userId,
                    'field': 'rdlogin_id',
                    'rdlogin_id': rdloginId,
                    'csrfmiddlewaretoken': csrf_token
                },
                success: function(response) {
                    var selectedText = row.find('select[name="rdlogin"] option:selected').text();
                    row.find('.rdlogin-value').text(selectedText).show();
                    row.find('select[name="rdlogin"]').select2('destroy').hide();
                    row.find('.edit-rdlogin-btn').show();
                    row.find('.delete-rdlogin-btn').show();
                    row.find('.save-rdlogin-btn').hide();
                    row.find('.cancel-rdlogin-btn').hide();
                }
            });
        }
    });

    $('.save-vpn-btn').click(function() {
        var row = $(this).closest('tr');
        var userId = row.data('user-id');
        var vpnId = row.find('select[name="vpn"]').val();

        if (vpnId) {
            $.ajax({
                url: edit_user_url,
                method: 'POST',
                data: {
                    'ad_user_id': userId,
                    'field': 'vpn_id',
                    'vpn_id': vpnId,
                    'csrfmiddlewaretoken': csrf_token
                },
                success: function(response) {
                    var selectedText = row.find('select[name="vpn"] option:selected').text();
                    row.find('.vpn-value').text(selectedText).show();
                    row.find('select[name="vpn"]').select2('destroy').hide();
                    row.find('.edit-vpn-btn').show();
                    row.find('.delete-vpn-btn').show();
                    row.find('.save-vpn-btn').hide();
                    row.find('.cancel-vpn-btn').hide();
                }
            });
        }
    });

    $('.delete-rdlogin-btn').click(function() {
        var row = $(this).closest('tr');
        var userId = row.data('user-id');
        var rdloginValue = row.find('.rdlogin-value').text();

        if (rdloginValue !== '-') {
            $.ajax({
                url: edit_user_url,
                method: 'DELETE',
                contentType: 'application/json',
                data: JSON.stringify({
                    'ad_user_id': userId,
                    'field': 'rdlogin'
                }),
                headers: {
                    'X-CSRFToken': csrf_token
                },
                success: function(response) {
                    row.find('.rdlogin-value').text('-').show();
                    row.find('select[name="rdlogin"]').select2('destroy').hide();
                    row.find('.edit-rdlogin-btn').show();
                    row.find('.save-rdlogin-btn').hide();
                    row.find('.cancel-rdlogin-btn').hide();
                }
            });
        }
    });

    $('.delete-vpn-btn').click(function() {
        var row = $(this).closest('tr');
        var userId = row.data('user-id');
        var vpnValue = row.find('.vpn-value').text();

        if (vpnValue !== '-') {
            $.ajax({
                url: edit_user_url,
                method: 'DELETE',
                contentType: 'application/json',
                data: JSON.stringify({
                    'ad_user_id': userId,
                    'field': 'vpn'
                }),
                headers: {
                    'X-CSRFToken': csrf_token
                },
                success: function(response) {
                    row.find('.vpn-value').text('-').show();
                    row.find('select[name="vpn"]').select2('destroy').hide();
                    row.find('.edit-vpn-btn').show();
                    row.find('.save-vpn-btn').hide();
                    row.find('.cancel-vpn-btn').hide();
                }
            });
        }
    });
});
