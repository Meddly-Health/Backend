import datetime

import firebase_admin
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth, credentials

import config
from database import Database

cred = credentials.Certificate(config.firebase)
firebase_admin.initialize_app(cred)


async def authenticate(
    cred: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
    db=Depends(Database.get_db),
):
    if cred is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer authentication required",
        )

    try:
        decoded_token = auth.verify_id_token(cred.credentials)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials. {err}",
        )

    user = await db["user"].find_one({"user_id": decoded_token["user_id"]})
    if not user:
        # TODO: Define user creation
        user = {
            "user_id": decoded_token["user_id"],
            "email": decoded_token["email"],
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now(),
            "diseases": [],
            "supervisors": [],
            "supervised": [],
        }
        await db["user"].insert_one(user)
    return decoded_token
