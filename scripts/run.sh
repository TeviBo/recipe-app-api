#!/bin/sh
# Mockea nuestro archivo a sh file

# Con set -e lo que establecemos es que
# si algo falla en el siguiente comando que agregamos
# al script, va a fallar inmediatamente todo el script
# y no continua ejecutando el siguiente comando.
set -e

# Ejecutamos el comando que necesitamos para nuestra app
python manage.py
python manage.py collectstatic --noinput
python manage.py migrate

uwsgi --socket :9000 --workers 4 --master --enable-threads --module app.wsgi


