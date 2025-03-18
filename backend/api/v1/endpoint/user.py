from fastapi import FastAPI, HTTPException, UploadFile, Form, File, Body, Query, Header, Depends
from fastapi import APIRouter
import itertools

from schema import UserSignupDetails, UserLoginDetails, UserCheckingDetails
from utils import decrypt_text
from db import db_client

router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not Found"}},
)

@router.get("/")
async def system_check():
    """Check if the user-related functions are online and operational.

    Returns:
        dict: A dictionary with a message confirming the user functions are online.
    """
    return {"message": "User Functions Online"}

@router.post("/signup")
async def user_signup(user_details: UserSignupDetails = Body(...)):
    """Register a new user with the provided details.

    Args:
        user_details (UserSignupDetails): A schema containing username, first_name, last_name, and encrypted password.

    Returns:
        dict: A dictionary with a success flag, a message, and the user_id (if successful).

    Raises:
        HTTPException: If password decryption fails (status 404) or signup process encounters an error (status 404).
    """
    # Try to decrypt password
    try:
        password_decrypted = decrypt_text(user_details.password)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Error: <{e}>. Could not decrypt encrypted text during signup.")

    try:
        signup_response = db_client.create_user(
            user_details.username,
            user_details.first_name,
            user_details.last_name,
            password_decrypted
        )
        if signup_response['success']:
            return {
                "success": True,
                "message": "Account successfully created.",
                "user_id": signup_response['user_id']
            }
        else:
            return {
                "success": False,
                "message": "Account already existed.",
                "user_id": signup_response['user_id']
            }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Error: <{e}>. Signup process failed.")

@router.post("/login")
async def user_login(user_details: UserLoginDetails = Body(...)):
    """Authenticate a user with their username and password.

    Args:
        user_details (UserLoginDetails): A schema containing username and encrypted password.

    Returns:
        dict: A dictionary with a success flag, a message, and the user_id (if successful).

    Raises:
        HTTPException: If password decryption fails (status 404) or login process encounters an error (status 404).
    """
    # Try to decrypt password
    try:
        password_decrypted = decrypt_text(user_details.password)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Error: <{e}>. Could not decrypt encrypted password during login.")

    try:
        login_response = db_client.authenticate_user(user_details.username, password_decrypted)
        if login_response['success']:
            return {
                "success": True,
                "message": "Account successfully login.",
                "user_id": login_response['user_id']
            }
        else:
            return {
                "success": False,
                "message": "Failed to Login. Incorrect Username/Password.",
                "user_id": ""
            }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Error: <{e}>. Login process failed.")

@router.get("/get_user_details")
async def check_user_exist(user_details: UserCheckingDetails = Depends()):
    """Retrieve details of an existing user by their user ID.

    Args:
        user_details (UserCheckingDetails): A schema containing the user_id, provided via dependency injection.

    Returns:
        dict: A dictionary with a success flag, first_name, and last_name of the user.

    Raises:
        HTTPException: If retrieving user details fails (status 404).
    """
    print(user_details.user_id)

    try:
        user_details = db_client.get_user_details(user_details.user_id)
        return {
            "success": True,
            "first_name": user_details['first_name'],
            "last_name": user_details['last_name']
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Error: <{e}>. Could not get user details")