import json
from datetime import datetime

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import insert

from app.config import settings
from app.database import Base, async_session_maker, engine
from app.main import app as fastapi_app
from app.rolls.models import Rolls


@pytest.fixture(scope="function", autouse=True)
async def prepare_database():
    # Обязательно убеждаемся, что работаем с тестовой БД
    assert settings.MODE == "TEST"

    async with engine.begin() as conn:
        # Удаление всех заданных нами таблиц из БД
        await conn.run_sync(Base.metadata.drop_all)
        # Добавление всех заданных нами таблиц из БД
        await conn.run_sync(Base.metadata.create_all)

    def open_mock_json(model: str):
        with open(f"app/tests/mock_{model}.json", encoding="utf-8") as file:
            return json.load(file)

    rolls = open_mock_json("rolls")

    for roll in rolls:
        # SQLAlchemy не принимает дату в текстовом формате, поэтому форматируем к datetime
        roll["created_at"] = datetime.strptime(roll["created_at"], "%Y-%m-%d %H:%M:%S.%f")
        if roll["deleted_at"] is not None:
            roll["deleted_at"] = datetime.strptime(roll["deleted_at"], "%Y-%m-%d %H:%M:%S.%f")


    async with async_session_maker() as session:
        query = insert(Rolls).values(rolls)
        await session.execute(query)
        await session.commit()

@pytest.fixture(scope="function")
async def ac():
    "Асинхронный клиент для тестирования эндпоинтов"
    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as ac:
        yield ac