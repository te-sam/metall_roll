from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.rolls.dao import RollsDAO
from app.rolls.schemas import (
    RollCreate,
    RollFilter,
    RollResponse,
    RollStatisticsResponse,
)

router_rolls = APIRouter(prefix="/rolls", tags=["Руллоны"])


@router_rolls.post(
    "/", response_model=RollResponse, status_code=status.HTTP_201_CREATED
)
async def create_roll(roll_data: RollCreate):
    """
    Добавление нового рулона на склад.
    - **length**: Длина рулона (обязательный параметр).
    - **weight**: Вес рулона (обязательный параметр).
    """
    try:
        new_roll = await RollsDAO.add(
            length=roll_data.length,
            weight=roll_data.weight,
            created_at=datetime.now(),
            deleted_at=None,
        )
        return new_roll

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка базы данных: {str(e)}",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Неизвестная ошибка: {str(e)}",
        )


@router_rolls.delete("/{roll_id}", response_model=RollResponse)
async def delete_from_warehouse(roll_id: int):
    """
    Удаление рулона со склада.
    - **roll_id**: Уникальный идентификатор рулона.
    """
    try:
        deleted_roll = await RollsDAO.mark_as_deleted(roll_id)
        if not deleted_roll:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Рулон с id {roll_id} не найден или уже удален",
            )
        return deleted_roll

    except HTTPException:
        raise

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка целостности данных при удалении рулона",
        )

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка базы данных: {str(e)}",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Неизвестная ошибка: {str(e)}",
        )


@router_rolls.get("/", response_model=list[RollResponse])
async def get_rolls(
    id_min: int | None = Query(None, description="Минимальное значение id"),
    id_max: int | None = Query(None, description="Максимальное значение id"),
    weight_min: float | None = Query(None, description="Минимальный вес"),
    weight_max: float | None = Query(None, description="Максимальный вес"),
    length_min: float | None = Query(None, description="Минимальная длина"),
    length_max: float | None = Query(None, description="Максимальная длина"),
    created_at_min: datetime | None = Query(None, description="Минимальная дата добавления"),
    created_at_max: datetime | None = Query(None, description="Максимальная дата добавления"),
    deleted_at_min: datetime | None = Query(None, description="Минимальная дата удаления"),
    deleted_at_max: datetime | None = Query(None, description="Максимальная дата удаления"),
):
    """
    Получение списка рулонов со склада с фильтрацией.
    """
    try:
        filters = RollFilter(
            id_min=id_min,
            id_max=id_max,
            weight_min=weight_min,
            weight_max=weight_max,
            length_min=length_min,
            length_max=length_max,
            created_at_min=created_at_min,
            created_at_max=created_at_max,
            deleted_at_min=deleted_at_min,
            deleted_at_max=deleted_at_max,
        )
        rolls = await RollsDAO.find_all(filters)
        return rolls

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Некорректные параметры запроса: {str(e)}",
        )

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка базы данных: {str(e)}",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Неизвестная ошибка: {str(e)}",
        )


@router_rolls.get("/statistics", response_model=RollStatisticsResponse)
async def get_roll_statistics(
    start_date: datetime = Query(..., description="Начальная дата периода"),
    end_date: datetime = Query(..., description="Конечная дата периода"),
):
    """
    Получение статистики по рулонам за определённый период.
    """
    try:
        if end_date < start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Начальная дата больше конечной даты",
            )

        statistics = await RollsDAO.get_statistics(start_date, end_date)

        if not statistics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Статистика по рулонам за указанный период не найдена",
            )
        return statistics

    except HTTPException:
        raise

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Некорректные параметры запроса: {str(e)}",
        )

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка базы данных: {str(e)}",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Неизвестная ошибка: {str(e)}",
        )
