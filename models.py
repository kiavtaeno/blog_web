from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional

class TravelerBase(BaseModel):
    email: str
    username: str

class TravelerCreate(TravelerBase):
    password: str

    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Некорректный email')
        return v

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Пароль должен быть не менее 6 символов')
        return v

    @validator('username')
    def validate_username(cls, v):
        if len(v) < 2:
            raise ValueError('Имя пользователя слишком короткое')
        return v

class TravelerUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

class Traveler(TravelerBase):
    id: int
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True

class JourneyBase(BaseModel):
    destination: str
    story: str

class JourneyCreate(JourneyBase):
    travelerId: int

    @validator('destination')
    def validate_destination(cls, v):
        if len(v) < 2:
            raise ValueError('Название публикации слишком короткое')
        return v

    @validator('story')
    def validate_story(cls, v):
        if len(v) < 10:
            raise ValueError('Рассказ слишком короткий')
        return v

class JourneyUpdate(BaseModel):
    destination: Optional[str] = None
    story: Optional[str] = None

class Journey(JourneyBase):
    id: int
    travelerId: int
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True