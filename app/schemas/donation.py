from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator

from app.schemas.base import DonationBase, BaseModelMixin


class DonationCreate(DonationBase):
    """Схема для создания пожертвования."""

    comment: Optional[str] = Field(None, max_length=500)
    full_amount: int = Field(..., gt=0)

    class Config:
        extra = "forbid"

    @validator('full_amount')
    def validate_full_amount(cls, value):
        """Валидация суммы пожертвования."""
        if value <= 0:
            raise ValueError('Сумма пожертвования должна быть больше 0')
        return value


class DonationDB(BaseModelMixin, DonationBase):
    """Схема для вывода пожертвования из БД."""

    comment: Optional[str] = None
    full_amount: int

    class Config:
        from_attributes = True


class DonationUserDB(BaseModel):
    """Схема для вывода пожертвования пользователю (без sensitive данных)."""

    id: int
    comment: Optional[str] = None
    full_amount: int
    create_date: datetime

    class Config:
        from_attributes = True