from pydantic import BaseModel



class userInput(BaseModel):
    name: str
    email: str
    password: str

class userLogIn(BaseModel):
    email: str
    password: str 


class TodoResponse(BaseModel):
    content: str

class TodoInput(BaseModel):
    content: str



def todo_serializer(todo)-> dict:
    return {
        "_id" : str(todo["_id"]),
        "user_email": str(todo["user_email"]),
        "content": str(todo["task"]),
        "time_stamp": str(todo["time_stamp"])
    }

def todos_serializer(todos)-> list:
    return [todo_serializer(todo) for todo in todos]


def user_serializer(user)-> dict:
    return {
        "_id" : str(user["_id"]),
        "name": str(user["name"]),
        "email": str(user["email"]),
        "password": str(user["password"])
    }