from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.controllers.scrape_controller import router

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(router)

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
