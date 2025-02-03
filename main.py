from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import router

origins = [
    "http://127.0.0.1:8000",
    "http://localhost:8000"
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(router)

