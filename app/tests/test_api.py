from datetime import datetime

import pytest
from httpx import AsyncClient

from app.rolls.schemas import RollFilter


@pytest.mark.parametrize("payload, expected_status, expected_error", [
    ({"length": 100.0, "weight": 50.0}, 201, None),  # Успешное создание рулона
    ({"length": -10.0, "weight": 50.0}, 422, "value_error"),  # Некорректная длина
    ({"length": 100.0, "weight": -5.0}, 422, "value_error"),  # Некорректный вес
    ({"length": "сто", "weight": 5.0}, 422, "value_error"),  # Длина строкой
    ({}, 422, "value_error.missing"),  # Отсутствуют параметры
])
async def test_create_roll(ac: AsyncClient, payload, expected_status, expected_error):
    response = await ac.post("/rolls/", json=payload)

    assert response.status_code == expected_status

    if expected_error:
        assert "detail" in response.json()

@pytest.mark.parametrize("roll_id, expected_status", [
    (1, 200),  # Успешное удаление
    (9999, 404),  # Не найден
    (2, 404),  # Уже удален
    ('два', 422)  # Уже удален
])
async def test_delete_from_warehouse(ac: AsyncClient, roll_id, expected_status):
    response = await ac.delete(f"/rolls/{roll_id}")

    assert response.status_code == expected_status

    if response.status_code == 200:
        roll_data = response.json()
        assert roll_data["id"] == roll_id
        assert roll_data["deleted_at"] is not None  

@pytest.mark.parametrize("filters, expected_ids", [
    (RollFilter(), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]),  # Без фильтров
    (RollFilter(id_min=13), [13, 14]),  # Фильтр по min id
    (RollFilter(id_max=2), [1, 2]),  # Фильтр по max id
    (RollFilter(weight_min=50), [4, 7, 11, 12, 13, 14]),  # Фильтр по минимальному весу
    (RollFilter(weight_max=50), [1, 2, 3, 4, 5, 6, 8, 9, 10]),  # Фильтр по максимальному весу
    (RollFilter(length_min=25, length_max=150), [13, 14]),  # Фильтр по диапазону длины
    (RollFilter(created_at_min=datetime(2025, 3, 1)), [1, 3, 4, 5, 7, 8, 10, 12, 13]),  # Фильтр по дате создания (min)
    (RollFilter(created_at_max=datetime(2025, 3, 1)), [2, 6, 9, 11, 14]),  # Фильтр по дате создания (max)
    (RollFilter(deleted_at_min=datetime(2026, 1, 1)), [14]),  # Фильтр по дате удаления (min)
    (RollFilter(deleted_at_max=datetime(2025, 3, 5)), [3]),  # Фильтр по дате удаления (max)
    (RollFilter(weight_min=50, length_max=25), [4, 7, 11, 12, 13]),  # По двум параметрам
    (RollFilter(
        id_min=3,
        id_max=13,
        weight_min=10,
        weight_max=90,
        length_min=20,
        length_max=90,
        created_at_min=datetime(2023, 3, 6),
        created_at_max=datetime(2026, 3, 1),
        deleted_at_min=datetime(2025, 4, 16),
        deleted_at_max=datetime(2025, 6, 1)
    ), [12])  # Комбинированный фильтр
])
async def test_get_rolls(ac: AsyncClient, filters, expected_ids):
    query_params = {
        key: value.isoformat() if isinstance(value, datetime) else value
        for key, value in filters.model_dump(exclude_none=True).items()
    }

    response = await ac.get("/rolls/", params=query_params)

    assert response.status_code == 200

    roll_ids = [roll["id"] for roll in response.json()]
    assert set(roll_ids) == set(expected_ids), f"Ожидалось {expected_ids}, но получено {roll_ids}"

@pytest.mark.parametrize("start_date, end_date, expected_status, expected_response", [
    (datetime(2025, 1, 1), datetime(2025, 12, 31), 200, 
     {'total_added': 10, 
      'total_deleted': 10, 
      'avg_length': 18.4, 
      'avg_weight': 49.0, 
      'max_length': 30.0, 
      'min_length': 10.0, 
      'max_weight': 70.0, 
      'min_weight': 30.0, 
      'total_weight': 490.0, 
      'max_time_between_add_delete': 369.17745498842595, 
      'min_time_between_add_delete': 0.23277005787037036, 
      'day_min_rolls': '2025-03-02', 
      'day_max_rolls': '2025-03-02', 
      'day_min_weight': '2023-03-06', 
      'day_max_weight': '2025-01-01'}),

    (datetime(2023, 1, 1), datetime(2024, 1, 31), 200, 
     {'total_added': 1, 
      'total_deleted': 0, 
      'avg_length': 2.0, 
      'avg_weight': 13.0, 
      'max_length': 2.0, 
      'min_length': 2.0, 
      'max_weight': 13.0, 
      'min_weight': 13.0, 
      'total_weight': 13.0, 
      'max_time_between_add_delete': None, 
      'min_time_between_add_delete': None, 
      'day_min_rolls': '2023-03-06', 
      'day_max_rolls': '2023-03-06', 
      'day_min_weight': '2023-03-06', 
      'day_max_weight': '2023-03-06'}),
      
    (datetime(2025, 12, 31), datetime(2025, 1, 1), 400, None),  # Начальная дата больше конечной
    (datetime(2029, 1, 1), datetime(2030, 1, 2), 404, None),  # Нет данных за указанный период
])
async def test_get_roll_statistics(ac: AsyncClient, start_date, end_date, expected_status, expected_response,):
    response = await ac.get("/rolls/statistics", params={
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    })
    assert response.status_code == expected_status

    if expected_status == 200:
        assert response.json() == expected_response