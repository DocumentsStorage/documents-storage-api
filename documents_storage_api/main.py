
from os import getenv
from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from routers import default, accounts, document_types, documents, media
from mongoengine import connect, ConnectionFailure
from services.generate_admin_account import create_admin_account

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
