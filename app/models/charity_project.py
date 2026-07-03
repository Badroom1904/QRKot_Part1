from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Integer, String, Text, Boolean
from sqlalchemy.orm import validates

from app.core.db import Base


class CharityProject(Base):
    """Модель целевого проекта фонда QRKot."""

    __tablename__ = 'charityproject'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
    full_amount = Column(Integer, nullable=False)
    invested_amount = Column(Integer, default=0, nullable=False)
    fully_invested = Column(Boolean, default=False, nullable=False)
    create_date = Column(DateTime, default=datetime.now, nullable=False)
    close_date = Column(DateTime, nullable=True)

    @validates('name')
    def validate_name(self, key, value):
        """Валидация названия проекта (от 5 до 100 символов)."""
        if not value or not (5 <= len(value) <= 100):
            raise ValueError(
                'Название проекта должно содержать от 5 до 100 символов'
            )
        return value.strip()

    @validates('description')
    def validate_description(self, key, value):
        """Валидация описания проекта (не менее 10 символов)."""
        if not value or len(value.strip()) < 10:
            raise ValueError(
                'Описание проекта должно содержать не менее 10 символов'
            )
        return value.strip()

    @validates('full_amount')
    def validate_full_amount(self, key, value):
        """Валидация требуемой суммы (больше 0)."""
        if value <= 0:
            raise ValueError('Требуемая сумма должна быть больше 0')
        return value

    def __repr__(self):
        return f'<CharityProject {self.name}>'
