$(document).ready(function() {
    // Обработка клика по кнопке редактирования
    $('.edit-expiry-date-btn').click(function() {
      var userId = $(this).data('user-id');

      // Показываем поле для редактирования и кнопку сохранения
      $('#display_expiration_' + userId).hide();
      $('#input_expiration_' + userId).show();
      $('.save-expiry-date-btn[data-user-id="' + userId + '"]').show();
    });

    // Обработка клика по кнопке сохранения
    $('.save-expiry-date-btn').click(function() {
      var userId = $(this).data('user-id');
      var expirationDate = $('#input_expiration_' + userId).val();
      var accountType = $('#display_expiration_' + userId).data('account-type');
      var formattedDate = formatDateToDMY(expirationDate);

      if (!expirationDate) {
        $('#error_message_' + userId).text('Пожалуйста укажите дату.').show();
        return;
      } else {
        $('#error_message_' + userId).hide();
      }

      $.ajax({
        url: '/users/update-expiration-date/',
        type: 'POST',
        headers: {
          'X-CSRFToken': csrf_token
        },
        data: JSON.stringify({
          expiration_date: expirationDate,
          account_type: accountType,
          user_id: userId
        }),
        contentType: 'application/json',
        success: function(response) {
          if (response.success) {
            // Обновляем отображаемую дату
            $('#display_expiration_' + userId).text(formattedDate ? formattedDate : '');
            $('#display_expiration_' + userId).show();
            $('#input_expiration_' + userId).hide();
            $('.save-expiry-date-btn[data-user-id="' + userId + '"]').hide();
          } else {
            alert('Ошибка обновления даты.');
          }
        },
        error: function() {
          alert('Ошибка обновления даты.');
        }
      });
    });

    // Обработка клика по кнопке удаления
    $('.delete-expiry-date-btn').click(function() {
      var userId = $(this).data('user-id');
      var accountType = $('#display_expiration_' + userId).data('account-type');
      
      // Очищаем поле даты
      $('#input_expiration_' + userId).val('');

      // Отправляем запрос на сервер для очистки даты
      $.ajax({
        url: '/users/update-expiration-date/',
        type: 'POST',
        headers: {
          'X-CSRFToken': csrf_token
        },
        data: JSON.stringify({
          expiration_date: null,  // Устанавливаем null для удаления даты
          account_type: accountType,
          user_id: userId
        }),
        contentType: 'application/json',
        success: function(response) {
          if (response.success) {
            // Обновляем отображаемую дату
            $('#display_expiration_' + userId).text('');
            $('#display_expiration_' + userId).show();
            $('#input_expiration_' + userId).hide();
            $('.save-expiry-date-btn[data-user-id="' + userId + '"]').hide();
          } else {
            alert('Ошибка удаления даты.');
          }
        },
        error: function() {
          alert('Ошибка удаления даты.');
        }
      });
    });

  });

function formatDateToDMY(dateString) {
    if (!dateString) return '';

    var date = new Date(dateString);
    var day = ('0' + date.getDate()).slice(-2);
    var month = ('0' + (date.getMonth() + 1)).slice(-2);
    var year = date.getFullYear();

    return day + '.' + month + '.' + year;
}