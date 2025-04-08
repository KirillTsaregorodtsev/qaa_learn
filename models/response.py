from pydantic import BaseModel, EmailStr, field_validator, ConfigDict


class Data(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    avatar: str


class Support(BaseModel):
    url: str
    text: str

class User(BaseModel):
    data: Data
    support: Support

class UsersList(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int
    data: list[Data]
    support: Support

class UpdatedUser(BaseModel):
    name: str
    job: str
    updatedAt: str

class CreatedUser(BaseModel):
    model_config = ConfigDict(strict=True)

    id: int
    createdAt: str
    name: str
    job: str