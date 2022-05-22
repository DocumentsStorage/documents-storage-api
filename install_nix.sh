git clone https://github.com/DocumentsStorage/documents-storage-api.git documents-storage-api
git clone https://github.com/DocumentsStorage/documents-storage-ui.git documents-storage-ui

API_HOST=$1
export API_PORT=$2
export APP_PORT=$3

# Update API .env
printf "PYTHONPATH=documents_storage_api
DEBUG=False
TEST=False
DB_URL=mongodb://documents-storage-db:27017/documents-storage
HOST_IP=$API_HOST
API_HOST=0.0.0.0
API_PORT=$API_PORT
API_ORIGINS=['*']" > documents-storage-api/.env

# Update UI .env
printf "API_URL=http://$API_HOST:$API_PORT" > documents-storage-ui/.env

cd documents-storage-api
docker-compose up -d --build -f docker-compose.default.yml