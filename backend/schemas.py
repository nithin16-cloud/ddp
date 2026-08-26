from pydantic import BaseModel, EmailStr, ConfigDict
from models import UserRole


class UserSignup(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.patient


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    role: UserRole


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
