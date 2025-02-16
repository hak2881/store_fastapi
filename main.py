from fastapi import FastAPI, Header
from fastapi.responses import JSONResponse, Response

from database import init_db
from routes.orders import orders_router
from routes.products import products_router
from routes.users import users_router
from utils import utils_router

app = FastAPI()

app.include_router(products_router)
app.include_router(users_router)
app.include_router(orders_router)
app.include_router(utils_router)

@app.on_event("startup")
async def startup():
    await init_db()

responses = {
    "en": {"message": "Hello, welcome!"},
    "ko": {"message": "안녕하세요, 환영합니다!"},
    "fr": {"message": "Bonjour, bienvenue!"},
    "de": {"message": "Hallo, willkommen!"},
    "es": {"message": "iHola, bienvenido!"}
}


