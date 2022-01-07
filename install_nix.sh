git clone https://github.com/DocumentsStorage/documents-storage-api.git documents-storage-api
git clone https://github.com/DocumentsStorage/documents-storage-ui.git documents-storage-ui

DS_PATH=$1
API_HOST=$2
API_PORT=$3
APP_PORT=$4

# Variables
JWT_SECRET=$RANDOM

# Updated docker .env
printf "API_DIR=$DS_PATH/api
DB_DIR=$DS_PATH/db
API_PORT=$API_PORT
APP_PORT=$APP_PORT" > documents-storage-api/docker/.env


# Update API .env
printf "PYTHONPATH=documents_storage_api
DEBUG=False
DB_URL=mongodb://mongo-ds:27017/documents-storage
HOST_IP=$API_HOST
API_HOST=0.0.0.0
API_PORT=$API_PORT
API_ORIGINS=['*']
API_JWT_SECRET=$JWT_SECRET" > documents-storage-api/.env


# Update UI .env
printf "API_URL=http://$API_HOST:$API_PORT" > documents-storage-ui/.env


cd documents-storage-api/docker
docker-compose build
docker-compose up -d