FROM python:3.9-alpine3.13
LABEL maintainer="Daniel Goliszewski taafeenn@gmail.com"
LABEL version="0.8.4"
WORKDIR /usr/src/app/documents-storage-api
# Set user
RUN groupadd -r documents-storage && useradd --no-log-init -r -g documents-storage documents-storage
USER documents-storage
COPY . .
RUN apk add --no-cache musl-dev=1.2.2-r1 gcc=10.2.1_pre1-r3 libffi-dev=3.3-r2 git=2.30.3-r0
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir pytest==7.1.2 coverage==6.3.3
RUN printf "PYTHONPATH=documents_storage_api \n \
DEBUG=True \n \
DB_URL=mongodb://mongo-ds-test:27017/documents-storage \n \
HOST_IP=127.0.0.1 \n \
API_HOST=127.0.0.1 \n \
API_PORT=8000 \n \
API_ORIGINS=['http://localhost:5000', 'http://localhost:8000'] \n \
API_JWT_SECRET='test_secret'" > .env
CMD nohup sh -c "export PYTHONPATH=documents_storage_api && coverage run --source routers -m pytest && coverage report -m"