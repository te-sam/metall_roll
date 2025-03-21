from sqlalchemy import delete, insert, select, update

from app.database import async_session_maker


class BaseDAO:
    model = None


    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter_by(**filter_by)
            result = await session.execute(query)
            return result.mappings().one_or_none()

    @classmethod
    async def find_all(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter_by(**filter_by)
            result = await session.execute(query)
            return result.mappings().all()
    

    @classmethod
    async def add(cls, **data):
        query = insert(cls.model).values(**data).returning(cls.model.__table__.columns)
        async with async_session_maker() as session:
            result = await session.execute(query)
            await session.commit()
            return result.mappings().first()

    @classmethod
    async def delete(cls, **filter_by):
        async with async_session_maker() as session:
            query = delete(cls.model).filter_by(**filter_by).returning(cls.model.__table__.columns)
            result = await session.execute(query)
            await session.commit()
            return result.mappings().first()
    
    @classmethod
    async def update(cls, id: int, **update_values):
         async with async_session_maker() as session:
            query = update(cls.model).filter_by(id=id).values(**update_values).returning(cls.model.__table__.columns)
            result = await session.execute(query)
            await session.commit()
            return result.mappings().first()