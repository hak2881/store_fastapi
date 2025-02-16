import xml.etree.ElementTree as ET
from fastapi import  Header, APIRouter
from fastapi.responses import JSONResponse, Response

utils_router = APIRouter()

responses = {
    "en": {"message": "Hello, welcome!"},
    "ko": {"message": "안녕하세요, 환영합니다!"},
    "fr": {"message": "Bonjour, bienvenue!"},
    "de": {"message": "Hallo, willkommen!"},
    "es": {"message": "iHola, bienvenido!"}
}

@utils_router.get("/greet/")
async def greet(accept_language: str = Header("en")):
    return responses.get(accept_language, responses["en"])

@utils_router.get("/data/")
async def get_data(format: str="json"):
    data = {"message": "Hello, FastAPI"}

    if format == "xml":
        root = ET.Element("response")
        message = ET.SubElement(root, "message")
        message.text = data["message"]
        xml_str = ET.tostring(root, encoding="utf-8", method="xml")
        return Response(content=xml_str, media_type="application/xml")

    return JSONResponse(content=data)