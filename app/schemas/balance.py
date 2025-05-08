from pydantic import BaseModel, EmailStr


class Deposit(BaseModel):
    deposit: float