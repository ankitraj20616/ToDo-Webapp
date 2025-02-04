from fastapi import APIRouter,  HTTPException, Response, Cookie
from models import userInput, userLogIn, TodoInput, todos_serializer
from database import users_collection, todo_collection
from starlette import status
from utils import PasswordIncription
from config import setting
from datetime import timedelta
from auth import JWTAuthentication
from datetime import datetime


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
    user: dict = users_collection.find_one({"email": user_info.email})
    if user and PasswordIncription().verify_password(user.get("password") , user_info.password):
        expire_time = timedelta(minutes= setting.ASCESS_TOKEN_EXPIRE_MINUTES)
        jwt_token = JWTAuthentication().generate_token({"email": user.get("email")}, expire_time)
        jwt_token = jwt_token.decode("utf-8") if isinstance(jwt_token, bytes) else jwt_token
        return {"token": jwt_token}
    
    raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= "Incorrect email or password!")


@router.post("/routeProtected/{token}")
def routeProtected(jwt_token: str= Cookie(None)):
    payload: dict = JWTAuthentication().verify_token(jwt_token)
    if not payload or not payload.get("email"):
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= "Invalid token!")
    return {"message": f"Hello {payload.get('email')}, you have accessed a protected route."}

@router.post("/logIn")
def logIn(response: Response,user_info: userLogIn):
    token_response = loginJWTToken(user_info)
    token = token_response.get("token")
    if not token:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Token generation failed!")
    response.set_cookie(
        key= "jwt_token",
        value= token,
        httponly= True
    )
    message = routeProtected(token)
    return {"token": token, "message": message.get("message")}


@router.post("/insertToDo")
def insertToDo(new_todo: TodoInput, jwt_token: str = Cookie(None)):
    if not jwt_token:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= "You Should Log In First!")
    
    payload: dict = JWTAuthentication().verify_token(jwt_token)
    if not payload or not payload.get("email"):
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail= "LogIn Error! unable to extact email from current token.")
    user_email = payload.get("email")
    last_id = int(readTodo(jwt_token).get("todo")[-1].get("_id"))
    print(last_id)
    todo_collection.insert_one({"_id": last_id + 1,"user_email": user_email, "task": new_todo.content, "time_stamp": datetime.now().isoformat()})
    return {"message": "Todo item inserted successfully!", "email": user_email}

@router.get("/readTodos")
def readTodo(jwt_token: str = Cookie(None)):
    if not jwt_token:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail = "You Should Log In First!")
    payload: dict = JWTAuthentication().verify_token(jwt_token)
    if not payload or not payload.get("email"):
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail= "LogIn Error! unable to extact email from current token.")
    user_email = payload.get("email")
    all_todos = list(todo_collection.find({"user_email": user_email}))
    return {"todo": todos_serializer(all_todos)}

@router.delete("/deleteTodo")
def deleteTodo(_id: int, jwt_token: str= Cookie(None)):
    if not jwt_token:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= "You should login first!")
    payload: dict = JWTAuthentication().verify_token(jwt_token)
    if not payload or not payload.get("email"):
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail= "LogIn Error! unable to extact email from current token.")
    user_email = payload.get("email")
    todo_collection.delete_one({"_id": _id, "user_email": user_email})
    return {"_id": _id,"user_email": user_email, "message": "Deleted!"}

@router.put("/updateTodo")
def updateTodo(update_info: TodoInput, _id: int, jwt_token: str= Cookie(None)):
    if not jwt_token:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= "You should login first!")
    payload: dict = JWTAuthentication().verify_token(jwt_token)
    if not payload or not payload.get("email"):
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail= "LogIn Error! unable to extact email from current token.")
    user_email = payload.get("email")
    todo_collection.update_one({"_id": _id, "user_email": user_email}, {"$set": {"task": update_info.content}}, upsert= True)
    return {"_id": _id,"user_email": user_email, "message": "Updated!"}