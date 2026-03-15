from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.routes import router
from app.logging_config import setup_logging

setup_logging()

app = FastAPI()

app.include_router(router)

app.mount("/static", StaticFiles(directory="frontend"), name="static")

templates = Jinja2Templates(directory="frontend")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})