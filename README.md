# API для получения информции о комплектующих компьютеров Windows

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
    - установите nginx
    - отредактирует конфигурацию nginx, в файле `/etc/nginx/sites-available/dafault`
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
    - Создайте файл .env и запишите в него необходимые переменные окружения:
        - `POSTGRES_USER=django_user`
        - `POSTGRES_PASSWORD=mysecretpassword`
        - `POSTGRES_DB=django`
        - `DB_HOST=db`
        - `DB_PORT=5432`
        - `SECRET_KEY=Super_secret_key`
    - запустите `sudo docker compose up`
    - настройте автозапуск, напрмиер так `https://blog.site-home.ru/docker-compose-systemd.html`

### Опрос клиентов
Для сбора информации с клиентов можно использовать `invent_pc_api.ps1`, запускать с любой Windows-машины от пользователя имеющего административные права на клиенских ПК.

### Отправка с гипервизоров
Для отправки информации о виртуальных машинах можно использовать скрипт `vms.ps1`, запускать на сервере Hyper-V под админом.

### Планы по доработке
- Переписать вью-функции на вью-классы
- Использовать django-filters вместо условий во views.py
- Сделать форму фильтра по департаменту универсальной чтобы исключить дублирование кода(например в index и comps_by_item).

### Авторы
Денис Третьяков

[MIT License](https://opensource.org/licenses/MIT)
