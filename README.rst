Initial admin account credentials - username: ``admin``, password: ``documents-storage-supervisor``

# Developing (with poetry)
* Go to directory where you cloned repository
* Install dependencies ``poetry install``
* Enable shell with dependencies ``poetry shell``
* Copy .env.prod to .env and configure it
* Run ``python documents_storage_api/main.py``
* **API documentation is available under http://API_IP/docs**