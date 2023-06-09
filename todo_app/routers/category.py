import time
from todo_app.auth.config import current_active_user
from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from todo_app.schemas.entries import CategoryCreate, CategoryUpdate, CategoryRead
from todo_app.db.database import get_async_session
from todo_app.models.entries import Category

router = APIRouter(
    prefix='/API/category',
    tags=['Category']
)


@router.post('/create')
async def add_new_category(new_category: CategoryCreate = Depends(CategoryCreate.as_form),
                           session: AsyncSession = Depends(get_async_session)):
    statement = insert(Category).values(**new_category.dict()).returning(Category)
    result = await session.execute(statement)
    await session.commit()
    return result.scalars().first()


@router.get('/')
async def get_all_categories(session: AsyncSession = Depends(get_async_session), user=Depends(current_active_user)):
    result = await session.scalars(select(Category).where(Category.user_id == user.id))
    return result.all()


@router.get('/{cat_slug}', response_model=CategoryRead)
async def get_category(cat_slug: str, session: AsyncSession = Depends(get_async_session)):
    result = await session.scalars(select(Category).where(Category.slug == cat_slug))
    return result.first()


@router.put('/{cat_slug}/update')
async def update_category(cat_slug: str, update_category: CategoryUpdate = Depends(CategoryUpdate.as_form),
                          session: AsyncSession = Depends(get_async_session)):
    statement = update(Category).where(Category.slug == cat_slug).values(**update_category.dict()).returning(Category)
    result = await session.execute(statement)
    await session.commit()
    return result.scalars().first()


@router.delete('/{cat_slug}/delete')
async def delete_category(cat_slug: str, session: AsyncSession = Depends(get_async_session)):
    statement = delete(Category).where(Category.slug == cat_slug)
    await session.execute(statement)
    await session.commit()
    return {'status': 'success'}
