param([string]$API_HOST, [int]$API_PORT, [int]$APP_PORT)

git clone https://github.com/DocumentsStorage/documents-storage-api.git documents-storage-api
git clone https://github.com/DocumentsStorage/documents-storage-ui.git documents-storage-ui

# Updated docker .env
"API_PORT=$API_PORT
APP_PORT=$APP_PORT" | Out-File -Encoding utf8 -FilePath .\documents-storage-api\docker\.env


# Update API .env
"PYTHONPATH=documents_storage_api
DEBUG=False
TEST=False
DB_URL=mongodb://documents-storage-db:27017/documents-storage
HOST_IP=$API_HOST
API_HOST=0.0.0.0
API_PORT=$API_PORT
API_ORIGINS=['*']" | Out-File -Encoding utf8 -FilePath .\documents-storage-api\.env


# Update UI .env
"API_URL=http://${API_HOST}:${API_PORT}" | Out-File -Encoding utf8 -FilePath .\documents-storage-ui\.env

docker-compose up -d --build -f docker-compose.default.yml
