=================
Documents Storage
=================

Project enforces you with simple web-based app which allow you to easily manage documents.
For example storage important invoices, receipts, certificates, and also add scans of those documents.

---------------
Top Features 🚀
---------------
#. Create and modify documents 📄
#. Upload image or pdf files 💼
#. Download stored files 📥
#. Create own document types to streamline your workflow 🔧
#. Tagging system 🏷
#. Manage accounts 👨‍🔧
#. OpenAPI - connect anything to Documents Storage 📲

====================
DocumentsStorage API
====================

.. image:: https://codecov.io/gh/DocumentsStorage/documents-storage-api/branch/master/graph/badge.svg?token=7PH4PIYS54
    :target: https://codecov.io/gh/DocumentsStorage/documents-storage-api
.. image:: https://snyk.io/test/github/DocumentsStorage/documents-storage-api/badge.svg
    :target: https://snyk.io/test/github/DocumentsStorage/documents-storage-api

==============
Table Of Contents
==============
- `Installation`_.
    - `With docker prebuilt (recommended)`_.
    - `With docker building (A bit longer)`_.
    - `Standalone (Advanced)`_.
- `Update`_.
    - `Docker - prebuilt`_.
    - `Docker - built`_.
    - `Standalone`_.
- `Development`_.
    - `With poetry`_.
    - `Without poetry`_.
- `Testing`_.
    - `With Docker-Compose`_.
    - `Without Docker-Compose`_.

==============
Installation
==============

----------------------------------------------------------------------
With `docker prebuilt <https://docs.docker.com/engine/install/>`_ (recommended)
----------------------------------------------------------------------
1. Create docker-compose.yml file
::
  version: "3.3"
  services:
    documents-storage-api:
      container_name: documents-storage-api
      restart: always
      image: tafeen/documents-storage-api:v0.9.1
      hostname: documents-storage-api
      ports:
        - 8000:8000
      volumes:
        - documents_storage_data:/usr/src/app/documents-storage-api
      networks:
        - documents_storage_fe
        - documents_storage_be
    documents-storage-ui:
      container_name: documents-storage-ui
      restart: always
      image: tafeen/documents-storage-ui:v0.9.1
      ports:
        - 5000:5000
      networks:
        - documents_storage_fe
    documents-storage-db:
      container_name: documents-storage-db
      hostname: documents-storage-db
      restart: always
      image: mongo:5.0.5
      volumes:
        - documents_storage_db:/data/db
      networks:
        - documents_storage_be
  networks:
    documents_storage_fe:
    documents_storage_be:
  volumes:
    documents_storage_data:
    documents_storage_db:

2. Run within directory: ``docker-compose up -d``
3. Run ``docker container logs documents-storage-api`` to copy generated password
4. Go to http://localhost:5000/
5. Login to admin account with username: ``admin`` and generated password, after it, it is advised to change account password

----------------------------------------------------------------------
With `docker building <https://docs.docker.com/engine/install/>`_ (A bit longer)
----------------------------------------------------------------------
- Linux/macOS

  #. Run from terminal: ``bash <(curl -s https://raw.githubusercontent.com/DocumentsStorage/documents-storage-api/master/build_nix.sh) 'localhost' 5001 5000``
  #. Run ``docker container logs documents-storage-api`` to copy generated password
  #. Go to http://localhost:5000/
  #. Login to admin account with username: ``admin`` and generated password, after it, it is advised to change account password

- Windows

  #. Run from PowerShell: ``Invoke-WebRequest https://raw.githubusercontent.com/DocumentsStorage/documents-storage-api/master/build_windows.ps1 -OutFile .\build_windows.ps1; .\build_windows.ps1 'localhost' 5001 5000``
  #. Run ``docker container logs documents-storage-api`` to copy generated password
  #. Go to http://localhost:5000/
  #. Login to admin account with username: ``admin`` and generated password, after it, it is advised to change account password


--------------------------------
Standalone (Advanced)
--------------------------------
#. Install git, node, python3.9, mongoDB
#. Git clone ``https://github.com/DocumentsStorage/documents-storage-api`` to 'documents-storage-api'
#. Install requirements.txt in 'documents-storage-api'
#. Edit documents-storage-api/.env
#. Run ``python3 documents_storage_api/main.py``
#. Git clone ``https://github.com/DocumentsStorage/documents-storage-ui`` to 'documents-storage-ui'
#. Edit documents-storage-ui/.env
#. Install dependencies ``npm install``
#. Build UI ``npm run build``
#. Serve UI ``npm start``
#. Go to http://localhost:5000/
#. See documents-storage-api logs to copy generated password
#. Login to admin account with username: ``admin`` and generated password, after it, it is advised to change account password


======
Update
======
-----------------
Docker - prebuilt
-----------------
#. Go to docker-compose file
#. Update docker-compose.default.yml images versions
#. Run ``docker-compose -f docker-compose.default.yml up -d --build``

--------------
Docker - built
--------------
#. Go to documents-storage-api directory
#. Run ``docker-compose -f docker-compose.default.yml stop && docker-compose -f docker-compose.default.yml  rm && docker-compose -f docker-compose.default.yml up -d --build``
#. Update docker-compose.default.yml images versions
#. Run ``docker-compose -f docker-compose.default.yml up -d --build``

----------
Standalone 
----------
#. Go to documents-storage-api and backup data
#. Run in api and ui directory ``git checkout tags/v1.0.0`` (select tag version)
#. Reuse backuped data with new version of app

===========
Development
===========
**API documentation is available under http://API_IP/docs**

It is recommended to use tool `Poetry
<https://python-poetry.org/>`_ with python 3.9


-----------
With poetry
-----------
#. Pull repository to desired directory
#. Run ``poetry install``
#. Copy ``./documents_storage_api/.env.prod`` to ``./documents_storage_api/.env`` and edit to match your requirements
#. From repository directory run ``poetry shell`` and ``python documents_storage_api/main.py``

--------------
Without poetry
--------------
#. Setup python for version 3.9
#. Pull repository to desired directory
#. Install packages from requirements file
#. Copy ``./documents_storage_api/.env.prod`` to ``./documents_storage_api/.env`` and edit to match your requirements
#. From repository directory run ``python documents_storage_api/main.py``

-------
Testing
-------

-------------------
With Docker-Compose
-------------------
#. Go to ``tests`` directory and run
``docker-compose up --build --attach documents-storage-api-test --abort-on-container-exit && docker-compose rm -fsv && docker image rm tests_documents-storage-api-test && docker network rm tests_documents_storage_test``

----------------------
Without Docker-Compose
----------------------
#. Make sure you have installed API with steps listed before.
#. While tesiting export path for API files ``export PYTHONPATH=documents_storage_api``
#. Run command with poetry : ``poetry shell`` and run ``pytest``; or without poetry just run ``pytest``

==============
Special Thanks
==============
Replace_non_ascii.py - https://gist.github.com/AdoHaha/a76157c6de5155bf6b0adc77988724d9
