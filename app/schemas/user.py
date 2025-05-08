from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    login: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    login: str
    password: str


class User(BaseModel):
    email: EmailStr