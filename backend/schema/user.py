from pydantic import BaseModel, Field
from typing import Dict, List, Literal
import json

class UserSignupDetails(BaseModel):
    username: str
    first_name: str
    last_name: str
    password: str

class UserLoginDetails(BaseModel):
    username: str
    password: str

class UserCheckingDetails(BaseModel):
    user_id: str