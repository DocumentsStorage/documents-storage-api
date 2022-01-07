param([string]$DS_PATH, [string]$API_HOST, [int]$API_PORT, [int]$APP_PORT)

git clone https://github.com/DocumentsStorage/documents-storage-api.git documents-storage-api
git clone https://github.com/DocumentsStorage/documents-storage-ui.git documents-storage-ui

# Variables
$JWT_SECRET = Get-Random

# Updated docker .env
"API_DIR=$DS_PATH/api
DB_DIR=$DS_PATH/db
API_PORT=$API_PORT
APP_PORT=$APP_PORT" | Out-File -Encoding utf8 -FilePath .\documents-storage-api\docker\.env


# Update API .env
"PYTHONPATH=documents_storage_api
DEBUG=False
DB_URL=mongodb://mongo-ds:27017/documents-storage
HOST_IP=$API_HOST
API_HOST=0.0.0.0
API_PORT=$API_PORT
API_ORIGINS=['*']
API_JWT_SECRET=$JWT_SECRET" | Out-File -Encoding utf8 -FilePath .\documents-storage-api\.env


# Update UI .env
"API_URL=http://${API_HOST}:${API_PORT}" | Out-File -Encoding utf8 -FilePath .\documents-storage-ui\.env

cd documents-storage-api/docker
docker-compose build
docker-compose up -d