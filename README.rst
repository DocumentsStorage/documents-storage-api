--------------------
DocumentsStorage API
--------------------

.. image:: https://codecov.io/gh/DocumentsStorage/documents-storage-api/branch/master/graph/badge.svg?token=7PH4PIYS54
    :target: https://codecov.io/gh/DocumentsStorage/documents-storage-api
.. image:: https://snyk.io/test/github/DocumentsStorage/documents-storage-api/badge.svg
    :target: https://snyk.io/test/github/DocumentsStorage/documents-storage-api

==============
How to install
==============

----------------------------------------------------------------------
With `docker <https://docs.docker.com/engine/install/>`_ (recommended)
----------------------------------------------------------------------
- Linux/macOS

  #. Run from terminal: ``bash <(curl -s https://raw.githubusercontent.com/DocumentsStorage/documents-storage-api/master/install_nix.sh) './ds' 'localhost' 5001 5000``
  #. Go to http://localhost:5000/
  #. Run ``docker container logs documents-storage-api`` to copy generated password
  #. Login to admin account with username: ``admin`` and generated password, after it, it is advised to change account password

- Windows

  #. Run from PowerShell: ``Invoke-WebRequest https://raw.githubusercontent.com/DocumentsStorage/documents-storage-api/master/install_windows.ps1 -OutFile .\install_windows.ps1; .\install_windows.ps1 './ds' 'localhost' 5001 5000``
  #. Go to http://localhost:5000/
  #. Run ``docker container logs documents-storage-api`` to copy generated password
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
``docker-compose build && docker-compose up --attach documents-storage-api-test  -V --force-recreate --abort-on-container-exit``

--------------
Without Docker
--------------
#. Make sure you have installed API with steps listed before.
#. While tesiting export path for API files ``export PYTHONPATH=documents_storage_api``
#. Run command with poetry : ``poetry shell`` and run ``pytest``; or without poetry just run ``pytest``

==============
Special Thanks
==============
Replace_non_ascii.py - https://gist.github.com/AdoHaha/a76157c6de5155bf6b0adc77988724d9
