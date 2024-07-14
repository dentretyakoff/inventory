## Inventory - сервис инвентаризации компьютеров и учетных записей

- [Описание](#desc)
- [Стек технологий](#stack)
- [Авторы](#team)


### Описание <a id="desc"></a>

**Inventory** - это сервис, позволяющий собирать информацию о комплектующих компьютеров в сети, а также получать список учетных записей Active Directory и связанных с ними VPN и Wi-Fi Radius.

####Главная страница
На главной странице можно быстро найти ПК по имени и получить всю информацию о нем. Фильтр по департаментам позволяет узнать количество ПК или оборудования в конкретном отделе.

####Страница "Гипервизоры"
На странице "Гипервизоры" представлен список виртуальных машин на гипервизорах. Они отображаются в удобной таблице, где видно количество машин на каждом гипервизоре, их адаптеры и время работы.

####Страница "Учетные записи"
На странице "Учетные записи" можно удобно искать пользователей и связанные с ними учетные записи Wi-Fi и VPN. Данные обновляются по нажатию кнопки "Обновить данные".

Этот сервис позволяет эффективно управлять и контролировать оборудование и учетные записи в вашей сети.

### Стек технологий <a id="stack"></a>
Django
DRF

- Краткая инструкция:
    - клонируйте репозиторий: `git clone git@github.com:dentretyakoff/inventory.git`
    - установите docker
        ```
        sudo apt update
        sudo apt install curl
        curl -fSL https://get.docker.com -o get-docker.sh
        sudo sh ./get-docker.sh
        sudo apt-get install docker-compose-plugin
        ```
    - установите nginx `sudo apt install nginx`
    - отредактируйте конфигурацию nginx, в файле `/etc/nginx/sites-available/dafault`
        ```
        server {
            server_name 127.0.0.1 invent-pc.local;
            location /api/ {
            proxy_set_header Host $http_host;
            proxy_pass http://127.0.0.1:8000/api/;
            }
            location / {
                allow 127.0.0.1;
                allow 192.168.0.0/24;
                deny all;
                proxy_pass http://127.0.0.1:8000;
            }
        }

        ```
    - Перейдите в директорию проекта: `cd ваш-репозиторий`
    - Создайте файл `.env` и запишите в него необходимые переменные окружения по примеру `.env.example`
    - Запустите `sudo docker compose up`
    - Настройте автозапуск docker, напрмиер так `https://blog.site-home.ru/docker-compose-systemd.html`

### Настройка WinRM
1. Enable-PSRemoting -Force
2. winrm set winrm/config/service '@{AllowUnencrypted="true"}'
3. winrm set winrm/config/service/auth '@{Basic="true"}'
4. Set-Item WSMan:\localhost\Client\TrustedHosts -Value "hostname_or_IP"

### Опрос клиентов
Для сбора информации с клиентов можно использовать `invent_pc_api.ps1`, запускать с любой Windows-машины от пользователя имеющего административные права на клиенских ПК.

### Отправка с гипервизоров
Для отправки информации о виртуальных машинах можно использовать скрипт `vms.ps1`, запускать на сервере Hyper-V под админом.

### Планы по доработке
- Переписать вью-функции на вью-классы
- Использовать django-filters вместо условий во views.py
- Авторизация на всех страницах

### Авторы <a id="team"></a>
Денис Третьяков

[MIT License](https://opensource.org/licenses/MIT)
