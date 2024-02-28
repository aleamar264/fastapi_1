from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from database import engine
import models
from routers import auth, todos, admin, users
from tools.middleware import log_middleware

app = FastAPI()
app.add_middleware(BaseHTTPMiddleware, dispatch=log_middleware)

models.Base.metadata.create_all(bind=engine)


@app.get("/healthy", status_code=200)
def healt_check():
    return {"status": "Healthy"}


app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
