from datetime import datetime
from typing import List

from pydantic import Field, field_serializer, BaseModel, condecimal, computed_field, field_validator, EmailStr
import uuid



class UserSchema(BaseModel):

    user_id : str = Field(default_factory= lambda : str(uuid.uuid4()))
    username : str
    email : EmailStr
    password : str
    is_active : bool
    role : str = Field(default="user")


    @field_serializer("is_active")
    def is_active(self, value: bool) -> str:
        return "Yes" if value else "No"

class OrderSchema(BaseModel):
    username: str  = None
    total_price: condecimal(max_digits=65, decimal_places=2)
    is_paid: bool
    created_at: datetime = Field(default_factory=datetime.utcnow)  # 새로운 객체가 만들어질때마다 바뀌어야해서 factory를 써야함

    products : List[int]

    @field_serializer("is_paid")
    def serialize_is_paid(self, value: bool) -> str:
        return "Yes" if value else "No"

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime) -> str:
        return value.strftime("%Y-%m-%d %H:%M:%S")

    class Config:
        orm_mode = True

class ProductSchema(BaseModel):
    name : str
    price : float = None
    discount : float = None


    @field_validator("discount")
    @classmethod
    def validate_discount(cls, value):
        if 0 <= value <= 100:
            return value
        raise ValueError("Check discount range")

    @computed_field
    @property
    def final_price(self) -> float:
        if self.discount == 100.0:
            return 0
        return self.price * (1 - (self.discount or 0)/100)

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token : str
    token_type : str