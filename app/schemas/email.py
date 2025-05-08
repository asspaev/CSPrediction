from pydantic import BaseModel, EmailStr, ValidationError

class EmailCheck(BaseModel):
    email: EmailStr
