from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Integer, String, Text, Boolean

from app.core.db import Base


class Donation(Base):
    """Модель пожертвования фонда QRKot."""

    __tablename__ = 'donation'

    id = Column(Integer, primary_key=True, index=True)
    comment = Column(Text, nullable=True)
    full_amount = Column(Integer, nullable=False)
    invested_amount = Column(Integer, default=0, nullable=False)
    fully_invested = Column(Boolean, default=False, nullable=False)
    create_date = Column(DateTime, default=datetime.now, nullable=False)
    close_date = Column(DateTime, nullable=True)

    def __repr__(self):
        return f'<Donation {self.id} amount={self.full_amount}>'