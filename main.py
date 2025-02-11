from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from routers import router
from os.path import dirname, join
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

origins = [
    "http://127.0.0.1:8000",
    "http://localhost:8000"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

current_dir = dirname(__file__)
static  = join(current_dir, 'static')
templates = join(current_dir, 'templates')


app.include_router(router)

app.mount("/static", StaticFiles(directory= static), name= "static")
templates = Jinja2Templates(directory= templates)

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index_login.html", {"request": request})


@app.get("/dashboard")
def home(request: Request):
    return templates.TemplateResponse("index_dashboard.html", {"request": request})
