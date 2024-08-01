## Inventory - сервис инвентаризации компьютеров и учетных записей

- [Описание](#desc)
- [Стек технологий](#stack)
- [Запуск проекта](#start)
  - [Генерация ENCRYPTION_KEY](#prep-encryption-key)
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
- клонируйте репозиторий: `git clone <ваш репозиторий>`
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

### Генерация ENCRYPTION_KEY <a id="prep-encryption-key"></a>
Для успешного шифрования паролей внешних сервисов необходимо заполнить переменную `ENCRYPTION_KEY` в файле `.env`.

Команда для генерации ключа:
```
docker compose exec backend python manage.py generate_key
```
Пример заполнения ключа
```
# Ключ для шифрования паролей сервисов
ENCRYPTION_KEY='wfFouqX4-6O-Eqv6nLzRXiVYVgEj-Vfp9PVRF-6fLWQ='
```
*Если вы утратили ключ, необходимо сгенерировать новый и перезаполнить все пароли сервисов.

### Настройка WinRM <a id="winrm"></a>
На сервере откуда планируется получать учетные записи Radius создайте пользователя `inventory` с правми администратора и в PowerShell выполните следующие команды:
```
Enable-PSRemoting -Force
winrm set winrm/config/service/auth '@{Negotiate="true"}'
```
Если используете HTTPS соединение, загрузите ваш сертификат в `Cert:\LocalMachine\My` и привяжите его отпечаток к Listener
```
# Получает отпечаток сертификата
$cert = Get-ChildItem -Path Cert:\LocalMachine\My | Where-Object { $_.Subject -like "*inventory.yourdomen.com*" }
# Удаляет все Listener(опционально)
Get-ChildItem wsman:\localhost\Listener\ | Where-Object -Property Keys -like 'Transport=HTTP*' | Remove-Item -Recurse
# Создает Listener и привязывает к нему ваш сертификат
New-Item -Path WSMan:\localhost\Listener\ -Transport HTTPS -Address * -CertificateThumbPrint $cert.Thumbprint -Force
```
* Если используете самоподписной сертификат, расположите корневой сертифкат в директории с проектом, рядом с файлом manage.py


### Настройка RouterOS <a id="router-os"></a>
На сервере с RouterOS или Mikrotik создайте пользователя с правами на чтение.
```
/user add name=inventory group=read password=yourpassword
```
Включите api в Mikrotik
```
/ip service set numbers="api" disabled="no"
```

### Опрос клиентов <a id="win-computers"></a>
Для сбора информации с клиентов можно использовать `invent_pc_api.ps1`, запускать с любой Windows-машины от пользователя имеющего административные права на клиенских ПК.

### Отправка с гипервизоров <a id="vms"></a>
Для отправки информации о виртуальных машинах можно использовать скрипт `vms.ps1`, запускать на сервере Hyper-V под админом.

### Планы по доработке <a id="development-plans"></a>
- Использовать django-filters вместо условий во views.py
- Авторизация на всех страницах
- Переписать взаимодействие с сервисами с помощью абстрактного класса ExternalService

### Авторы <a id="team"></a>
Денис Третьяков

[MIT License](https://opensource.org/licenses/MIT)
