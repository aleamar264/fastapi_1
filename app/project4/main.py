from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from database import engine
import models
from routers import auth, todos, admin, users
from tools.middleware import log_middleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.add_middleware(BaseHTTPMiddleware, dispatch=log_middleware)

models.Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/healthy", status_code=200)
def healt_check():
    return {"status": "Healthy"}


@app.get("/not-found", response_class=HTMLResponse)
async def not_found():
    return templates.TemplateResponse("not-found.html")


app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
