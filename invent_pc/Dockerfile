FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN apt-get update
RUN apt-get -y install libldap2-dev libsasl2-dev ldap-utils
RUN pip install gunicorn==20.1.0
RUN pip install -r requirements.txt --no-cache-dir
COPY . .
