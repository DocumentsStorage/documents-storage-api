
from os import getenv
from dotenv import load_dotenv

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import default, accounts

from mongoengine import connect, ConnectionFailure
from services.generate_admin_account import create_admin_account


load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=getenv("API_ORIGINS"),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.debug = getenv("DEBUG")


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


# Routes
app.include_router(default.router)
app.include_router(accounts.router)


if __name__ == "__main__":
    uvicorn.run(
    "main:app",
    host=getenv("API_HOST"),
    port=int(getenv("API_PORT")),
    log_level="info",
    reload=getenv("DEBUG")
    )

