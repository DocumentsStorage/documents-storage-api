from os import getenv
from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from starlette.middleware.cors import CORSMiddleware
from routers import default, accounts, document_types, documents, media, tags, bulk_export
from mongoengine import connect, ConnectionFailure
from services.initial_setup import create_admin_account, create_predefined_document_types
from pathlib import Path
from single_source import get_version

path_to_pyproject_dir = Path(__file__).parent.parent
__version__ = get_version(__name__, path_to_pyproject_dir, default_return=None)

load_dotenv()

app = FastAPI()
app.debug = getenv("DEBUG")


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(default.router)
app.include_router(accounts.router)
app.include_router(document_types.router)
app.include_router(documents.router)
app.include_router(media.router)
app.include_router(tags.router)
app.include_router(bulk_export.router)


# OpenAPI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="",
        version="",
        routes=app.routes,
    )
    openapi_schema["info"] = {
        "title": "Documents Storage API",
        "version": __version__,
        "description": "This is a OpenAPI documentation for Documents Storage API",
        "contact": {
            "name": "Github repository",
            "url": "https://github.com/DocumentsStorage/documents-storage-api",
        },
        "license": {
            "name": "GNU General Public License version 2",
            "url": "https://www.gnu.org/licenses/old-licenses/gpl-2.0-standalone.html"
        },
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# Connect with database
try:
    connection = connect(
        alias="default",
        host=getenv("DB_URL"),
        serverSelectionTimeoutMS=3000
    )
    connection = connection.server_info()
    print("Connected with database")
    create_admin_account()
    create_predefined_document_types()
except ConnectionFailure as error:
    print("Could not connect with database")
    print(error)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=getenv("API_HOST"),
        port=int(getenv("API_PORT")),
        log_level="info",
        reload=getenv("DEBUG")
    )
