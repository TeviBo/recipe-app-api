# Recipe App Api

Recipe API project

-------------

## Info

### Github Actions (Jobs)

Github actions son jobs que se ejecutan en un pipeline dependiendo de un trigger. Se escriben en yml como los archivos de docker

```yml
name: Checks

on: [push]

jobs:
  test-lint:
    name: Test and Lint
    runs-on: ubuntu-20.04
    steps:
      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKERHUB_USER }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      - name: Checkout
        uses: actions/checkout@v3
      - name: Test
        run: docker-compose run --rm app sh -c "python manage.py test"
      - name: Lint
        run: docker-compose run --rm app sh -c "flake8"
```

### Glosario

- **name**: con esta regla le damos un nombre al job el cual se mostrara en la UI del repo.
- **on**: con esta regla, especificamos el trigger que disparara nuestro job.
- **jobs**: aqui especificamos todos los jobs que queremos en nuestro pipeline.
  - **name**: idem que el name mencionado anteriormente, sirve para darle un nombre a nuestro job.
  - **runs-on**: especificamos en que os se ejecutara nuestro job.
  - **steps**: una lista con todos los pasos que se ejecutaran en nuestro job.
    - **name**: mismo que lo anterior, declaramos un nombre para el paso.
    - **uses**: permite utilizar acciones ya existentes de github actions, en este caso utilizamos la accion login de docker-hub y enviamos el username y password almacenados en los secretos del repositorio
    - **with**: especificamos que argumentos utilizara dicho hook. En este caso le enviamos username y password los cuales establecimos como secretos en nuestro repositorio.

### Containers

#### Dockerfile

En nuestro dockerfile especificamos toda la configuracion para la construccion de la imagen de nuestra app.

***Como buena practica***, se deben mantener las imagenes lo mas livianas posible

```Docker
#! Intentar mantener las imagenes de docker lo mas livianas posible
FROM python:3.9-alpine3.13

LABEL maintainer="Esteban Bobbiesi"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app

WORKDIR /app

EXPOSE 8000

ARG DEV=false
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
    build-base postgresql-dev musl-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
    then /py/bin/pip install -r /tmp/requirements.dev.txt; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \
    --disabled-password \
    --no-create-home \
    django-user

# Agregamos /py/bin al path de linux
ENV PATH="/py/bin:$PATH"

# Especificamos el usuario que vamos a usar, todo lo de arriba lo ejecuta el usuario root y luego elejimos utilizar 'django-user'
USER django-user
```

##### Glosario

- **FROM**: con esta regla especificamos la imagen sobre la cual se va a construir nuestro servicio.
- **LABEL**: sirve para darle una etiqueta a nuestra imagen.
- **ENV**: para declarar variables de entorno.
- **COPY**: para copiar archivos de nuestro directorio al directorio de la vm dentro del contenedor.
- **WORKDIR**: con esta regla especificamos nuestro directorio de trabajo.
- **EXPOSE**: sirve para exponer un puerto dentro del contenedor.
- **ARG**: sirve para declarar argumentos.
- **RUN**: sirve para ejecutar comandos sh en la vm dentro del contenedor.
- **USER**: sirve para especificar el usuario que utilizara la vm para ejecutar comandos.

#### Docker Compose

Docker Compose es una herramienta que se utiliza para definir y ejecutar aplicaciones multi-contenedor en Docker. Permite definir la configuración de varios contenedores Docker en un archivo YAML y luego iniciar y detener todos los contenedores con un solo comando.

En lugar de tener que configurar cada contenedor individualmente, Docker Compose permite definir la configuración completa de la aplicación en un solo archivo, lo que facilita la creación y la gestión de aplicaciones complejas. Además, Docker Compose permite especificar las dependencias entre contenedores, lo que asegura que los contenedores se inicien en el orden correcto. Lo cual nos permite que nuestro contenedor sea lo mas liviano posible

Una **buena practica** de docker es limpiar las dependencias que solo se necesitan para instalacion de paquetes por lo cual en nuestro docker podemos definir dependencias a limpiar.

*Ver comando en el apartado de DB

##### Glosario

```yml
version: "3.9"
services:
  app:
    build:
      context: .
      args:
        - DEV=true
    ports:
      - "8000:8000"
    volumes:
      - ./app:/app
    command: sh -c "python manage.py runserver 0.0.0.0:8000"
    environment:
      - DB_HOST=db
      - DB_NAME=devdb
      - DB_USER=devuser
      - DB_PASS=bobbiesi796
    depends_on:
      - db
  db:
    image: postgres:13-alpine
    volumes:
      - dev-db-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=devdb
      - POSTGRES_USER=devuser
      - POSTGRES_PASSWORD=bobbiesi796

volumes:
  dev-db-data:
```

Comenzamos declarando la version, esto se hace por definicion y tiene que estar si o si.

Luego procedemos a declarar los servicios que daran forma a nuestra app (Definimos la arquitectura). Dentro de esta accion, definimos 2 servicios: app y db. App contendra todas las reglas para que nuestra app funcione correctamente en el entorno virtual.

- build: aqui declaramos el contexto en el que se construira nuestro servicio app y los argumentos del entorno

- ports: mapeamos un puerto de nuestra maquina local con un puerto dentro de la maquina del contenedor. En este caso, mapeamos el puerto 8000 local contra el puerto 8000 del contenedor, no necesariamente tienen que ser los 2 iguales
- volumes: aqui especificamos el directorio que se mapeara al contenedor. En este caso, estamos especificando que nuestro directorio app que se encuentra dentro de la raiz, se mapee al directorio /app de nuestro contenedor
- command: con esta regla podemos ejecutar comandos sh dentro del contenedor. En este caso ejecutamos el comando para levantar el servidor
- environment: aqui especificamos todas las variables de entorno para nuestra app. Se pueden definir como esta en esta en la porcion de codigo de arriba o indicando un archivo de entorno de la siguiente manera

```docker
env_file:
      - ../app/.env (aqui especificar el path al archivo de entorno)
```

depends_on: con este comando especificamos si el servicio depende de otro. Lo que hara docker con esto es esperar a que el otro servicio este corriendo correctamente para levantar el cual tenga definido esta regla.

image: con esta regla especificamos la imagen de docker que queremos que se pulee. En este caso seleccionamos la imagen **postgres:13-alpine** como nuestra imagen de bd. Esto lo que hara es pullear de dockerhub la imagen correspondiente.

-------------

### Database configuration

Se necesita de un adaptador para conectar python con la bd, dicho adapter es ***psycopg2***
opciones:
psycopg2-binary: recomendado para entorno local de desarrollo pero no para prod
psycopg2: compila desde el codigo fuente. Por detras se compila para el os especifico en el que se esta ejecutando.
Requiere dependencias adicionales instaladas en el os

```py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME':  os.environ.get('DB_NAME'),
        'HOST': os.environ.get('DB_HOST'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASS'),
    }
}
```

#### Dependencias adicionales requeridas

- C compiler
- python3-dev
- libpq-dev

#### Paquetes equivalentes para la imagen Alpine de postgres

- postgresql-client
- build-base
- postgresql-dev
- musl-dev

Para instalar las dependencias necesarias para nuestra db, dentro del archivo Dockerfile, debemos agregar lo siguiente:
Debajo de la linea donde upgradeamos pip, agregamos '&& \\' para especificarle a la terminal que vamos a ejecutar mas codigo en un salto de linea al final y debajo colocamos lo siguiente:

```sh
apk add --update --no-cache postgresql-client \
apk add --update --no-cache --virtual .tmp-build-dev \
  build-base postgresql-dev musl-dev && \
```

Luego, mas abajo, especificamente despues de borrar la carpeta tmp/, agregamos '&& \\' y colocamos lo siguiente:

```sh
apk del .tmp-build-deps && \
```

De esta manera, completamos lo que mencionamos en el apartado de Docker. Limpiamos las dependencias que solo se necesitan para instalar el cliente, en este caso, de postgres
