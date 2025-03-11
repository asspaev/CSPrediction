from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Dict

from core import settings
from models import db_helper
from schemas import UserLogin
from utils import create_access_token
from servises.user import auth_user


router = APIRouter(
    prefix=settings.api.v1.menu,
)

