from passlib.context import CryptContext
from fastapi import HTTPException
from starlette import status
class PasswordIncription:
    def __init__(self):
        self.pwd_context = CryptContext(schemes= ["bcrypt"], deprecated= "auto")

    def password_hashing(self, password: str)-> str:
        return self.pwd_context.hash(password)
    
    def verify_password(self, hashed_pass: str, user_pass: str)-> bool:
        try:
            return self.pwd_context.verify(user_pass, hashed_pass)
        except Exception as e:
            raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail= f"Password verification error:- {e}")