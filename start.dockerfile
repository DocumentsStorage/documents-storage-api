FROM python:3.9-alpine3.13
LABEL maintainer="Daniel Goliszewski taafeenn@gmail.com"
LABEL version="0.9.1"
WORKDIR /usr/src/app/documents-storage-api

RUN apk add --no-cache musl-dev=1.2.2-r1 gcc=10.2.1_pre1-r3 libffi-dev=3.3-r2 git=2.30.3-r0 curl=7.79.1-r1

HEALTHCHECK CMD curl --fail http://0.0.0.0:8000/ping || exit 1

# Set env
ARG HOST_IP
ENV HOST_IP ${HOST_IP}

COPY . .

# Set user
RUN addgroup -S documents-storage && adduser -u 1500 -S documents-storage -G documents-storage
RUN chown -R 1500:1500 /usr/src/app/documents-storage-api
USER documents-storage


RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
CMD printf " \
DEBUG=False \n \
TEST=False \n \
DB_URL=mongodb://documents-storage-db:27017/documents-storage \n \
API_HOST=0.0.0.0 \n \
API_PORT=8000 \n \
API_ORIGINS=['*'] \n \
HOST_IP=${HOST_IP}" > .env ; python documents_storage_api/main.py