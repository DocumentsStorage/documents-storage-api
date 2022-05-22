FROM python:3.9-alpine3.13
LABEL maintainer="Daniel Goliszewski taafeenn@gmail.com"
LABEL version="0.9.1"
WORKDIR /usr/src/app/documents-storage-api

RUN apk add --no-cache musl-dev=1.2.2-r1 gcc=10.2.1_pre1-r3 libffi-dev=3.3-r2 git=2.30.3-r0

# Set env
ENV HOST_IP="localhost"
ENV API_HOST="0.0.0.0"

COPY . .

# Append env to file
RUN printf "PYTHONPATH=documents_storage_api \n \
DEBUG=False \n \
TEST=False \n \
DB_URL=mongodb://documents-storage-db:27017/documents-storage \n \
HOST_IP=$HOST_IP \n \
API_HOST=$API_HOST \n \
API_PORT=8000 \n \
API_ORIGINS=['*']" > .env

# Set user
RUN addgroup -S documents-storage && adduser -u 1500 -S documents-storage -G documents-storage
RUN chown 1500:1500 /usr/src/app/documents-storage-api
USER documents-storage

RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
CMD ["python", "documents_storage_api/main.py"]