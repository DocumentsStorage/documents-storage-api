FROM python:3.9-alpine3.13
MAINTAINER Daniel Goliszewski "taafeenn@gmail.com"
LABEL version="0.8.4"
WORKDIR /usr/src/app/documents-storage-api
COPY requirements.txt ./
RUN apk add --update musl-dev gcc libffi-dev git
RUN pip install -r requirements.txt
RUN pip install pytest
RUN pip install coverage
COPY . .
RUN printf "PYTHONPATH=documents_storage_api \n \
DEBUG=True \n \
DB_URL=mongodb://mongo-ds-test:27017/documents-storage \n \
HOST_IP=127.0.0.1 \n \
API_HOST=127.0.0.1 \n \
API_PORT=8000 \n \
API_ORIGINS=['http://localhost:5000', 'http://localhost:8000'] \n \
API_JWT_SECRET='test_secret'" > .env
CMD nohup sh -c "export PYTHONPATH=documents_storage_api && coverage run --source routers -m pytest && coverage report -m"