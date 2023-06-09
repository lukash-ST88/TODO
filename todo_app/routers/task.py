import time

from fastapi import APIRouter, Depends
from todo_app.auth.config import current_active_user
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from todo_app.schemas.entries import TaskCreate, TaskUpdate, TaskRead
from todo_app.db.database import get_async_session
from todo_app.models.entries import Task, Theme, Category
from sqlalchemy import desc

router = APIRouter(
    prefix='/API/task',
    tags=['Task']
)


@router.post('/create')
async def add_new_task(new_task: TaskCreate = Depends(TaskCreate.as_form),
                       session: AsyncSession = Depends(get_async_session)):
    statement = insert(Task).values(**new_task.dict()).returning(Task)
    result = await session.execute(statement)
    await session.commit()
    return result.scalars().first()


@router.get('/')
async def get_all_tasks(session: AsyncSession = Depends(get_async_session), user=Depends(current_active_user)):
    result = await session.scalars(select(Task).where(Task.user_id == user.id).order_by(desc(Task.creation_date)))
    return result.all()


@router.get('/cat/{cat_slug}')
async def get_tasks_by_cat(cat_slug: str, session: AsyncSession = Depends(get_async_session),
                           user=Depends(current_active_user)):
    result = await session.scalars(
        select(Task).join(Theme, Task.theme_id == Theme.id).join(Theme.cat).where(Category.slug == cat_slug).where(
            Task.user_id == user.id).order_by(
            desc(Task.creation_date)
        )
    )
    return result.all()



@router.get('/theme/{theme_slug}')
async def get_tasks_by_theme(theme_slug: str, session: AsyncSession = Depends(get_async_session),
                             user=Depends(current_active_user)):
    result = await session.scalars(
        select(Task).join(Theme, Task.theme_id == Theme.id).where(Theme.slug == theme_slug).where(
            Task.user_id == user.id).order_by(
            desc(Task.creation_date)
        )
    )
    return result.all()


@router.get('/{task_slug}', response_model=TaskRead)
async def get_task(task_slug: str, session: AsyncSession = Depends(get_async_session)):
    result = await session.scalars(select(Task).where(Task.slug == task_slug))
    return result.first()


@router.put('/{task_slug}/update')
async def update_task(task_slug: str, update_task: TaskUpdate = Depends(TaskUpdate.as_form),
                      session: AsyncSession = Depends(get_async_session)):
    statement = update(Task).where(Task.slug == task_slug).values(**update_task.dict()).returning(Task)
    result = await session.execute(statement)
    await session.commit()
    return result.scalars().first()


@router.delete('/{task_slug}/delete')
async def delete_task(task_slug: str, session: AsyncSession = Depends(get_async_session)):
    statement = delete(Task).where(Task.slug == task_slug)
    await session.execute(statement)
    await session.commit()
    return {'status': 'success'}

# TODO: only for user
# TODO: slugify
# TODO: PAGES
# TODO: DATA LOGIC
# TODO: pagination
