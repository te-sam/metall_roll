from datetime import date, datetime
from decimal import Decimal

import pytest

from app.rolls.dao import RollsDAO
from app.rolls.schemas import RollFilter


@pytest.mark.parametrize("roll_id, expected", [
    (1, True),  # Успешное удаление
    (9999, False),  # ID не найден
    (2, False)  # Уже удалено
])
async def test_mark_as_deleted(roll_id, expected):
    result = await RollsDAO.mark_as_deleted(roll_id)
    print(result)
    
    if expected:
        assert result is not None
        assert result.id == roll_id
        assert result.deleted_at is not None
        assert isinstance(result.deleted_at, datetime)
    else:
        assert result is None

@pytest.mark.parametrize("filters, expected_ids", [
    (RollFilter(), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]),  # Без фильтров
    (RollFilter(id_min=13), [13, 14]),  # Фильтр по min id
    (RollFilter(id_max=2), [1, 2]),  # Фильтр по max id
    (RollFilter(weight_min=50), [4, 7, 11, 12, 13, 14]),  # Фильтр по минимальному весу
    (RollFilter(weight_max=50), [1, 2, 3, 4, 5, 6, 8, 9, 10]),  # Фильтр по максимальному весу
    (RollFilter(length_min=25, length_max=150), [13, 14]),  # Фильтр по диапазону длины
    (RollFilter(created_at_min=datetime(2025, 3, 1)), [1, 3, 4, 5, 7, 8, 10, 12, 13]),  # Фильтр по дате создания
    (RollFilter(created_at_max=datetime(2025, 3, 1)), [2, 6, 9, 11, 14]),  # Фильтр по дате создания
    (RollFilter(deleted_at_min=datetime(2026, 1, 1)), [14]),  # Фильтр по дате удаления
    (RollFilter(deleted_at_max=datetime(2025, 3, 5)), [3]),  # Фильтр по дате удаления
    (RollFilter(weight_min=50, length_max=25), [4, 7, 11, 12, 13]),  # По двум параметрам
    (RollFilter(id_min = 3,
                id_max = 13,
                weight_min = 10,
                weight_max = 90,
                length_min = 20,
                length_max = 90,
                created_at_min = datetime(2023, 3, 6),
                created_at_max = datetime(2026, 3, 1),
                deleted_at_min = datetime(2025, 4, 16),
                deleted_at_max = datetime(2025, 6, 1)),
                [12]) # Комбинированный фильтр
            ])
async def test_find_all(filters, expected_ids):
    result = await RollsDAO.find_all(filters)
    result_ids = [roll.id for roll in result]
    print(set(result_ids))
    assert set(result_ids) == set(expected_ids)

@pytest.mark.parametrize("start_date, end_date, expected", [
    (datetime(2023, 1, 1), datetime(2025, 1, 31), 
     {'total_added': 5, 
      'total_deleted': 0, 
      'avg_length': Decimal('15.8'), 
      'avg_weight': Decimal('42.4'), 
      'max_length': Decimal('30.00'), 
      'min_length': Decimal('2.00'), 
      'max_weight': Decimal('70.00'), 
      'min_weight': Decimal('13.00'), 
      'total_weight': Decimal('212.00'), 
      'max_time_between_add_delete': 369.17745498842595, 
      'min_time_between_add_delete': 365.0, 
      'day_min_rolls': date(2024, 3, 11), 
      'day_max_rolls': date(2024, 3, 11), 
      'day_min_weight': date(2023, 3, 6), 
      'day_max_weight': date(2025, 1, 1)}),

    (datetime(2023, 1, 1), datetime(2026, 1, 31), 
    {'total_added': 14,
     'total_deleted': 11, 
     'avg_length': Decimal('16.6428571428571429'), 
     'avg_weight': Decimal('45.1428571428571429'), 
     'max_length': Decimal('30.00'), 
     'min_length': Decimal('2.00'), 
     'max_weight': Decimal('70.00'), 
     'min_weight': Decimal('13.00'), 
     'total_weight': Decimal('632.00'), 
     'max_time_between_add_delete': 369.17745498842595, 
     'min_time_between_add_delete': 0.23277005787037036, 
     'day_min_rolls': date(2025, 3, 2), 
     'day_max_rolls': date(2025, 3, 2), 
     'day_min_weight': date(2023, 3, 6), 
     'day_max_weight': date(2025, 1, 1)}),
    
    (datetime(2023, 1, 1), datetime(2024, 1, 31), 
    {'total_added': 1, 
     'total_deleted': 0, 
     'avg_length': Decimal('2'), 
     'avg_weight': Decimal('13'), 
     'max_length': Decimal('2.00'), 
     'min_length': Decimal('2.00'), 
     'max_weight': Decimal('13.00'), 
     'min_weight': Decimal('13.00'), 'total_weight': Decimal('13.00'), 
     'max_time_between_add_delete': None, 
     'min_time_between_add_delete': None, 
     'day_min_rolls': date(2023, 3, 6), 
     'day_max_rolls': date(2023, 3, 6), 
     'day_min_weight': date(2023, 3, 6), 
     'day_max_weight': date(2023, 3, 6)}),
    
    (datetime(2029, 1, 1), datetime(2026, 1, 31), None),
    (datetime(2029, 1, 1), datetime(2030, 1, 31), None),
])
async def test_get_statistics(start_date, end_date, expected):
    result = await RollsDAO.get_statistics(start_date, end_date)
    print(result)
    assert result == expected

