## Inventory - сервис инвентаризации компьютеров и учетных записей

- [Описание](#desc)
- [Стек технологий](#stack)
- [Запуск проекта](#start)
- [Настройка WinRM](#winrm)
- [Настройка RouterOS](#router-os)
- [Опрос клиентов](#win-computers)
- [Отправка с гипервизоров](#vms)
- [Планы по доработке](#development-plans)
- [Авторы](#team)


### Описание <a id="desc"></a>

**Inventory** - это сервис, позволяющий собирать информацию о комплектующих компьютеров в сети, а также получать список учетных записей Active Directory и связанных с ними VPN и Wi-Fi Radius.

#### Главная страница
На главной странице можно быстро найти ПК по имени и получить всю информацию о нем. Фильтр по департаментам позволяет узнать количество ПК или оборудования в конкретном отделе.

#### Страница "Гипервизоры"
На странице "Гипервизоры" представлен список виртуальных машин на гипервизорах. Они отображаются в удобной таблице, где видно количество машин на каждом гипервизоре, их адаптеры и время работы.

#### Страница "Учетные записи"
На странице "Учетные записи" можно удобно искать пользователей и связанные с ними учетные записи Wi-Fi и VPN. Данные обновляются по нажатию кнопки "Обновить данные".

Этот сервис позволяет эффективно управлять и контролировать оборудование и учетные записи в вашей сети.

### Стек технологий <a id="stack"></a>
 - [Python 3.9](https://github.com/python/cpython/tree/3.9) Язык программирования, на котором построен проект.
 - [Django 3.2.16](https://www.djangoproject.com/) Веб-фреймворк на языке Python, который упрощает создание веб-приложений.
 - [Django REST framework 3.12.4](https://www.django-rest-framework.org/) Набор инструментов для создания веб-API на основе Django.
 - [requests 2.26.0](https://pypi.org/project/requests/) Библиотека для отправки HTTP-запросов на языке Python.
 - [python-dotenv 1.0.0](https://pypi.org/project/python-dotenv/) Библиотека для загрузки переменных окружения из файла .env.
 - [psycopg2-binary 2.9.3](https://www.psycopg.org/) Адаптер PostgreSQL для языка программирования Python.
 - [django-filter 2.4.0](https://django-filter.readthedocs.io/en/stable/) Библиотека для фильтрации запросов на основе Django.
 - [ldap3 2.9.1](https://ldap3.readthedocs.io/) Библиотека для работы с LDAP на языке Python.
 - [RouterOS-api 0.18.1](https://github.com/socialwifi/RouterOS-api) Библиотека для взаимодействия с API RouterOS.
 - [pywinrm 0.4.3](https://github.com/diyan/pywinrm) Библиотека для удаленного управления Windows через WinRM (Windows Remote Management).

### Запуск проекта <a id="start"></a>
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
   server_name 127.0.0.1 inventory.local;
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
- Перейдите в директорию проекта: `cd inventory`
- Создайте файл `.env` и запишите в него необходимые переменные окружения по примеру `.env.example`
- Запустите `sudo docker compose up -d`
- Настройте автозапуск docker, напрмиер так `https://blog.site-home.ru/docker-compose-systemd.html`
Приложение доступно по адресу http://localhost/

### Настройка WinRM <a id="winrm"></a>
На сервере откуда планируется получать пользователей Radius создайте пользователй `inventory` с правми администратора и в PowerShell выполните следующие команды:
```
Enable-PSRemoting -Force
winrm set winrm/config/service '@{AllowUnencrypted="true"}'
winrm set winrm/config/service/auth '@{Basic="true"}'
Set-Item WSMan:\localhost\Client\TrustedHosts -Value <укажите IP сервера>
```

### Настройка RouterOS <a id="router-os"></a>
На сервере с RouterOS или Mikrotik создайте пользователя с правами на чтение.
```
/user add name=inventory group=read password=yourpassword
```
Включите api в Mikrotik
```
/user add name=readuser group=read password=yourpasswor
```

### Опрос клиентов <a id="win-computers"></a>
Для сбора информации с клиентов можно использовать `invent_pc_api.ps1`, запускать с любой Windows-машины от пользователя имеющего административные права на клиенских ПК.

### Отправка с гипервизоров <a id="vms"></a>
Для отправки информации о виртуальных машинах можно использовать скрипт `vms.ps1`, запускать на сервере Hyper-V под админом.

### Планы по доработке <a id="development-plans"></a>
- Переписать вью-функции на вью-классы
- Использовать django-filters вместо условий во views.py
- Авторизация на всех страницах

### Авторы <a id="team"></a>
Денис Третьяков

[MIT License](https://opensource.org/licenses/MIT)
