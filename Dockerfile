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
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
    then /py/bin/pip install -r /tmp/requirements.dev.txt; \
    fi && \
    rm -rf /tmp && \
    adduser \
    --disabled-password \
    --no-create-home \
    django-user

# Agregamos /py/bin al path de linux
ENV PATH="/py/bin:$PATH"

# Especificamos el usuario que vamos a usar, todo lo de arriba lo ejecuta el usuario root y luego elejimos utilizar 'django-user'
USER django-user