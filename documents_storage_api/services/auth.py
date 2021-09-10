from os import getenv
from base64 import b64encode
import datetime
import jwt

from dotenv import load_dotenv
load_dotenv()

JWT_SECRET = getenv("API_JWT_SECRET")
JWT_SECRET_ENCODED = b64encode(JWT_SECRET.encode("utf-8"))
JWT_EXP_MINUTES = 90


def jwt_authenticate(client_id: str, rank: str):
    '''Get JWT token'''
    token = jwt.encode(
        {
            "client_id": client_id,
            "rank": rank,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=JWT_EXP_MINUTES)
        },
        JWT_SECRET_ENCODED,
        algorithm="HS256"
    )

    return token


def jwt_authorize(jwt_token):
    '''Check JWT token'''
    try:
        token = jwt.decode(jwt_token, JWT_SECRET_ENCODED, algorithms=["HS256"])
        return token
    except Exception as e:
        print(e)
        return False
