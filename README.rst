| Initial admin account credentials:
| username: ``admin``
| password: ``documents-storage-supervisor``

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
#. Make sure you have installed API with steps listed before.
#. While tesiting export path for API files ``export PYTHONPATH=documents_storage_api``
#. Run command with poetry : ``poetry shell`` and run ``pytest``; or without poetry just run ``pytest``