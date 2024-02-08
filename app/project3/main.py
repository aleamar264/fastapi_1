from fastapi import FastAPI
import models
from database import engine
from routers import auth, todos, admin, users
from tools.middleware import log_middleware
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI()
app.add_middleware(BaseHTTPMiddleware, dispatch=log_middleware)

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
