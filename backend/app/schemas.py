from datetime import date
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


class InputModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class RegisterInput(InputModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginInput(InputModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class HotelInput(InputModel):
    name: str = Field(min_length=2, max_length=160)
    description: str = Field(default="", max_length=4000)
    address: str = Field(min_length=3, max_length=300)
    city: str = Field(min_length=2, max_length=100)
    country: str = Field(default="", max_length=100)
    contact: str = Field(default="", max_length=100)
    rating: float = Field(default=0, ge=0, le=5)
    amenities: str = Field(default="", max_length=1000)


class RoomInput(InputModel):
    hotel_id: int = Field(gt=0)
    room_type_id: int = Field(gt=0)
    room_number: str = Field(min_length=1, max_length=20)
    floor: int = Field(default=1, ge=0)
    status: str = Field(default="available", pattern="^(available|maintenance|inactive)$")
    price: float | None = Field(default=None, ge=0)


class RoomTypeInput(InputModel):
    name: str = Field(min_length=2, max_length=100)
    description: str = Field(default="", max_length=2000)
    capacity: int = Field(gt=0, le=20)
    base_price: float = Field(ge=0)


class BookingInput(InputModel):
    room_id: int = Field(gt=0)
    check_in: date
    check_out: date
    guests: int = Field(default=1, gt=0, le=20)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.check_out <= self.check_in:
            raise ValueError("check_out must be after check_in")
        if self.check_in < date.today():
            raise ValueError("check_in cannot be in the past")
        return self
