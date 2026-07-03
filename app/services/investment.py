from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import CharityProject, Donation


async def invest_donations_to_projects(
    session: AsyncSession,
    donation: Donation
) -> None:
    """
    Распределяет пожертвование по открытым проектам.
    
    Алгоритм:
    1. Находит все открытые проекты (fully_invested=False), 
       отсортированные по дате создания (самые старые первыми)
    2. Распределяет сумму пожертвования по проектам по очереди
    3. Закрывает проекты, которые набрали нужную сумму
    4. Закрывает пожертвование, если все деньги распределены
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        donation: Объект пожертвования для распределения
    """
    # Находим все открытые проекты, сортируем по дате создания
    query = select(CharityProject).where(
        CharityProject.fully_invested == False
    ).order_by(CharityProject.create_date.asc())
    
    result = await session.execute(query)
    open_projects = result.scalars().all()
    
    if not open_projects:
        # Если нет открытых проектов, пожертвование остаётся нераспределённым
        return
    
    # Сумма для распределения
    # Убеждаемся, что invested_amount не None
    invested_amount = donation.invested_amount or 0
    remaining_amount = donation.full_amount - invested_amount
    
    if remaining_amount <= 0:
        # Если пожертвование уже полностью распределено
        return
    
    for project in open_projects:
        # Сколько ещё нужно проекту
        project_invested = project.invested_amount or 0
        needed_amount = project.full_amount - project_invested
        
        if needed_amount <= 0:
            continue
        
        # Рассчитываем сумму для инвестирования в этот проект
        if remaining_amount >= needed_amount:
            # Пожертвование покрывает всю оставшуюся сумму проекта
            invest_amount = needed_amount
            project.invested_amount = project.full_amount
            project.fully_invested = True
            project.close_date = datetime.now()
        else:
            # Пожертвование не полностью покрывает проект
            invest_amount = remaining_amount
            project.invested_amount = (project.invested_amount or 0) + invest_amount
            # Проект остаётся открытым
        
        # Обновляем пожертвование
        donation.invested_amount = (donation.invested_amount or 0) + invest_amount
        remaining_amount -= invest_amount
        
        # Проверяем, полностью ли распределено пожертвование
        if donation.invested_amount >= donation.full_amount:
            donation.fully_invested = True
            donation.close_date = datetime.now()
            break
    
    # Сохраняем изменения в сессии (коммит будет выполнен вызывающей функцией)
    session.add(donation)
    for project in open_projects:
        session.add(project)


async def invest_free_donations_to_project(
    session: AsyncSession,
    project: CharityProject
) -> None:
    """
    Распределяет свободные пожертвования в новый проект.
    
    Алгоритм:
    1. Находит все пожертвования с нераспределёнными средствами
       (fully_invested=False), отсортированные по дате создания
    2. Распределяет их суммы в новый проект по очереди
    3. Закрывает пожертвования, которые полностью распределены
    4. Закрывает проект, если набрана нужная сумма
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        project: Объект проекта для инвестирования
    """
    query = select(Donation).where(
        Donation.fully_invested == False
    ).order_by(Donation.create_date.asc())

    result = await session.execute(query)
    open_donations = result.scalars().all()

    if not open_donations:
        return

    invested_amount = project.invested_amount or 0
    needed_amount = project.full_amount - invested_amount

    if needed_amount <= 0:
        return

    for donation in open_donations:
        donation_invested = donation.invested_amount or 0
        remaining_donation_amount = donation.full_amount - donation_invested

        if remaining_donation_amount <= 0:
            continue

        if remaining_donation_amount >= needed_amount:
            invest_amount = needed_amount
            project.invested_amount = project.full_amount
            project.fully_invested = True
            project.close_date = datetime.now()
        else:
            invest_amount = remaining_donation_amount
            project.invested_amount += invest_amount

        donation.invested_amount = (donation.invested_amount or 0) + invest_amount
        needed_amount -= invest_amount

        if donation.invested_amount >= donation.full_amount:
            donation.fully_invested = True
            donation.close_date = datetime.now()

        if project.fully_invested:
            break

    session.add(project)
    for donation in open_donations:
        session.add(donation)
