import sys

sys.path.append("..")

from fastapi import status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi import Depends, APIRouter, Request, Form
import models
from database import engine, session_
from sqlalchemy.orm import Session
from pydantic import BaseModel
from dependencies import get_current_user
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/users", tags=["users"], responses={404: {"description": "Not Found"}}
)
