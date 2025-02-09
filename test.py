from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from main import app
from database import get_todo_collection, get_users_collection
from models import userInput, userLogIn, TodoInput
import models
from auth import JWTAuthentication
from utils import PasswordIncription
import pytest
from pymongo.collection import Collection
import routers

client = TestClient(app)


@pytest.fixture(scope= "function")
def setup_db(mocker):
    mock_user_collection: Collection = MagicMock()
    mock_todo_collection: Collection = MagicMock()

    app.dependency_overrides[get_todo_collection] = lambda: mock_todo_collection
    app.dependency_overrides[get_users_collection] = lambda: mock_user_collection
    assert app.dependency_overrides[get_todo_collection]() is mock_todo_collection
    assert app.dependency_overrides[get_users_collection]() is mock_user_collection
    mock_user_collection.delete_many({})
    mock_todo_collection.delete_many({})

    return mock_user_collection, mock_todo_collection

    

def test_sign_up(setup_db):
    mock_user_collection, _ = setup_db
    
    user_info = userInput(name= "Test User", email= "test@gmail.com", password= "password")
    mock_user_collection.find_one.return_value = None

    with patch.object(PasswordIncription, "password_hashing", return_value= "hashed_password"):
        response = client.post("/signUp", json= user_info.model_dump())
    assert response.status_code == 200, response.text
    assert response.json() == {"message": "New User Insertion Done!"}

    mock_user_collection.insert_one.assert_called_once_with({"name": "Test User", "email": "test@gmail.com", "password": "hashed_password"})

    
def test_generate_jwt_token(setup_db):
    mock_user_collection, _ = setup_db

    user_info = userLogIn(email= "test@gmail.com", password= "password")
    mock_user_collection.find_one.return_value = {"email": "test@gmail.com", "password": "hashed_password"}

    with patch.object(PasswordIncription, "verify_password", return_value = True):
        with patch.object(JWTAuthentication, "generate_token", return_value = "test_jwt_token"):
            response = client.post("/generate_jwt_token", json= user_info.model_dump())
    assert response.status_code == 200
    assert response.json() == {"token": "test_jwt_token"}

def test_route_protected(setup_db):
    with patch.object(JWTAuthentication, "verify_token", return_value= {"email": "test@gmail.com"}):
        client.cookies.set("jwt_token", "valid_token")
        response = client.post("/routeProtected")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello test@gmail.com, you have accessed a protected route."}
    
def test_login(setup_db):
    mock_user_collection, _ = setup_db
    user_info = userLogIn(email= "test@gmail.com", password= "password")
    mock_user_collection.find_one.return_value = {"email": "test@gmail.com", "password": "hashed_password"}

    with patch.object(routers, "loginJWTToken", return_value = {"token": "test_jwt_token"}):
        with patch.object(routers, "routeProtected", return_value = {"message": f"Hello test@gmail.com, you have accessed a protected route."}):
            response = client.post("/logIn", json= user_info.model_dump())
    print(response.status_code ,response.json())
    assert response.status_code == 200
    assert "token" in response.json() 

def test_insert_todo(setup_db):
    _, mock_todo_collection = setup_db
    new_todo = TodoInput(content= "New Task")
    with patch.object(JWTAuthentication, "verify_token", return_value= {"email": "test@gmail.com"}):
        response = client.post("/insertToDo", json= new_todo.model_dump(), cookies= {"jwt_token": "valid_token"})
    
    assert response.status_code == 200
    assert response.json() == {"message": "Todo item inserted successfully!", "email": "test@gmail.com"}

def test_read_todo(setup_db):
    _, mock_todo_collection = setup_db
    mock_todo_collection.find.return_value = [{"_id": 1, "user_email": "test@gmail.com", "task": "New Task", "time_stamp": "ifijis"}]

    with patch.object(JWTAuthentication, "verify_token", return_value = {"email": "test@gmail.com"}):
        response = client.get("/readTodos", cookies= {"jwt_token": "valid_token"})

    assert response.status_code == 200
    assert "todo" in response.json()

def test_delete_todo(setup_db):
    _, mock_todo_collection = setup_db
    with patch.object(JWTAuthentication, "verify_token", return_value = {"email": "test@gmail.com"}):
        response = client.delete("/deleteTodo", params= {"_id": 1}, cookies= {"jwt_token": "valid_token"})
    assert response.status_code == 200
    assert response.json() == {"_id": 1,"user_email": "test@gmail.com", "message": "Deleted!"}

def test_update_todo(setup_db):
    _, mock_todo_collection = setup_db
    update_info = TodoInput(content= "Updated Todo")
    with patch.object(JWTAuthentication, "verify_token", return_value = {"email": "test@gmail.com"}):
        response = client.put("/updateTodo", json= update_info.model_dump(), params= {"_id": 1}, cookies= {"jwt_token": "valid_token"})
    
    assert response.status_code == 200
    assert response.json() == {"_id": 1,"user_email": "test@gmail.com", "message": "Updated!"}
