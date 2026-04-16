from pydantic import BaseModel, EmailStr

class UserLogin(BaseModel):
    email: EmailStr
    senha: str