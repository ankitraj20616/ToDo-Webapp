from fastapi import APIRouter,  HTTPException, Response, Cookie
from models import userInput, userLogIn
from database import users_collection, todo_collection
from starlette import status
from utils import PasswordIncription
from config import setting
from datetime import timedelta
from auth import JWTAuthentication

router = APIRouter()


@router.get("/")
def test():
    return "App Loaded!"

@router.post("/signUp")
def signUp(new_user: userInput):
    is_already_registered = users_collection.find_one({"email": new_user.email})
    if is_already_registered:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail= "Email already registered!")
    new_user.password = PasswordIncription().password_hashing(new_user.password)
    users_collection.insert_one({"name": new_user.name, "email": new_user.email, "password": new_user.password})
    return {"message": "New User Insertion Done!"}

@router.post("/generate_jwt_token")
def loginJWTToken(user_info: userLogIn):
    users = users_collection.find({"email": user_info.email})
    for user in users:
        if PasswordIncription().verify_password(user.get("password") , user_info.password):
            expire_time = timedelta(minutes= setting.ASCESS_TOKEN_EXPIRE_MINUTES)
            jwt_token = JWTAuthentication().generate_token({"email": user.get("email")}, expire_time)
            return jwt_token
    
    raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= "Incorrect email or password!")


@router.post("/routeProtected/{token}")
def routeProtected(jwt_token: str= Cookie(None)):
    payload: dict = JWTAuthentication().verify_token(jwt_token)
    if not payload or not payload.get("email"):
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= "Invalid token!")
    return {"message": f"Hello {payload.get('email')}, you have accessed a protected route."}

@router.post("/logIn")
def logIn(response: Response,user_info: userLogIn):
    token = loginJWTToken(user_info)
    response.set_cookie(
        key= "jwt_token",
        value= token,
        httponly= True
    )
    message = routeProtected(token)
    return {"token": token, "message": message.get("message")}