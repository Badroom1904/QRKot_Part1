from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.db import get_async_session
from app.models import Donation
from app.schemas import DonationCreate, DonationDB, DonationUserDB
from app.services import invest_donations_to_projects

router = APIRouter()


@router.get(
    "/",
    response_model=List[DonationDB],
    response_model_exclude_none=True,
    summary="Получить список всех пожертвований",
    description="Возвращает список всех пожертвований в Фонде.",
)
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session),
) -> List[DonationDB]:
    """Получить все пожертвования."""
    query = select(Donation).order_by(Donation.create_date.asc())
    result = await session.execute(query)
    return result.scalars().all()


@router.post(
    "/",
    response_model=DonationUserDB,
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
    summary="Сделать пожертвование",
    description="Создаёт новое пожертвование и автоматически распределяет "
                "его по открытым проектам.",
)
async def create_donation(
    donation_in: DonationCreate,
    session: AsyncSession = Depends(get_async_session),
) -> DonationUserDB:
    """Создать новое пожертвование."""
    new_donation = Donation(**donation_in.dict())
    session.add(new_donation)

    await invest_donations_to_projects(session, new_donation)

    await session.commit()
    await session.refresh(new_donation)

    return new_donation


@router.get(
    "/my",
    response_model=List[DonationUserDB],
    response_model_exclude_none=True,
    summary="Получить мои пожертвования",
    description="Возвращает список пожертвований текущего пользователя.",
)
async def get_my_donations(
    session: AsyncSession = Depends(get_async_session),
) -> List[DonationUserDB]:
    """
    Получить пожертвования текущего пользователя.
    
    В текущей версии возвращает все пожертвования, так как
    аутентификация ещё не реализована.
    """
    # В будущем здесь будет фильтрация по текущему пользователю
    query = select(Donation).order_by(Donation.create_date.asc())
    result = await session.execute(query)
    return result.scalars().all()
