from datetime import datetime

from sqlalchemy import and_, func, or_, select, update

from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.rolls.models import Rolls
from app.rolls.schemas import RollFilter


class RollsDAO(BaseDAO):
    model = Rolls

    @classmethod
    async def mark_as_deleted(cls, roll_id: int):
        async with async_session_maker() as session:
            query = (
                update(Rolls)
                .where((Rolls.id == roll_id) & (Rolls.deleted_at.is_(None)))
                .values(deleted_at=datetime.now())
                .returning(Rolls)
            )
            result = await session.execute(query)
            await session.commit()
            return result.scalar_one_or_none()
    
    @classmethod
    async def find_all(cls, filters: RollFilter):
        """
        Получает список рулонов с учетом фильтров.
        Фильтры применяются только к тем параметрам, которые переданы.
        """
        async with async_session_maker() as session:
            query = select(Rolls)
            
            # Создаем список условий для фильтрации
            conditions = []
            
            if filters.id_min is not None:
                conditions.append(Rolls.id >= filters.id_min)
            if filters.id_max is not None:
                conditions.append(Rolls.id <= filters.id_max)
            if filters.weight_min is not None:
                conditions.append(Rolls.weight >= filters.weight_min)
            if filters.weight_max is not None:
                conditions.append(Rolls.weight <= filters.weight_max)
            if filters.length_min is not None:
                conditions.append(Rolls.length >= filters.length_min)
            if filters.length_max is not None:
                conditions.append(Rolls.length <= filters.length_max)
            if filters.created_at_min is not None:
                conditions.append(Rolls.created_at >= filters.created_at_min)
            if filters.created_at_max is not None:
                conditions.append(Rolls.created_at <= filters.created_at_max)
            if filters.deleted_at_min is not None:
                conditions.append(Rolls.deleted_at >= filters.deleted_at_min)
            if filters.deleted_at_max is not None:
                conditions.append(Rolls.deleted_at <= filters.deleted_at_max)
            
            if conditions:
                query = query.where(and_(*conditions))
            
            result = await session.execute(query)
            return result.scalars().all()
        
    @classmethod
    async def get_statistics(cls, start_date: datetime, end_date: datetime):
        async with async_session_maker() as session:
            # Проверяем, есть ли рулоны в указанный период
            total_rolls_query = select(func.count()).where(
                or_(
                    # Рулоны, созданные в указанный период
                    and_(
                        Rolls.created_at >= start_date,
                        Rolls.created_at <= end_date
                    ),
                    # Рулоны, удалённые в указанный период
                    and_(
                        Rolls.deleted_at >= start_date,
                        Rolls.deleted_at <= end_date
                    ),
                )
            )
            total_rolls = (await session.execute(total_rolls_query)).scalar_one()
            
            if not total_rolls:
                return None
            
            # Количество добавленных рулонов
            added_query = select(func.count()).where(
                and_(
                    Rolls.created_at >= start_date,
                    Rolls.created_at <= end_date
                )
            )
            total_added = (await session.execute(added_query)).scalar_one()
            
            # Количество удалённых рулонов
            deleted_query = select(func.count()).where(
                and_(
                    Rolls.deleted_at >= start_date,
                    Rolls.deleted_at <= end_date
                )
            )
            total_deleted = (await session.execute(deleted_query)).scalar_one()
            
            # Средняя длина и вес
            avg_length_weight_query = select(
                func.avg(Rolls.length).label("avg_length"),
                func.avg(Rolls.weight).label("avg_weight")
            ).where(
                and_(
                    Rolls.created_at <= end_date,
                    or_(
                        Rolls.deleted_at.is_(None),
                        Rolls.deleted_at >= start_date
                    ),
                    Rolls.created_at >= start_date,
                    Rolls.created_at >= start_date
                )
            )
            avg_result = (await session.execute(avg_length_weight_query)).one()
            avg_length = avg_result.avg_length
            avg_weight = avg_result.avg_weight
            
            # Максимальная и минимальная длина и вес
            max_min_length_weight_query = select(
                func.max(Rolls.length).label("max_length"),
                func.min(Rolls.length).label("min_length"),
                func.max(Rolls.weight).label("max_weight"),
                func.min(Rolls.weight).label("min_weight")
            ).where(
                and_(
                    Rolls.created_at <= end_date,
                    or_(
                        Rolls.deleted_at.is_(None),
                        Rolls.deleted_at >= start_date
                    ),
                    Rolls.created_at >= start_date
                )
            )
            max_min_result = (await session.execute(max_min_length_weight_query)).one()
            max_length = max_min_result.max_length
            min_length = max_min_result.min_length
            max_weight = max_min_result.max_weight
            min_weight = max_min_result.min_weight
            
            # Суммарный вес
            total_weight_query = select(func.sum(Rolls.weight)).where(
                and_(
                    Rolls.created_at <= end_date,
                    or_(
                        Rolls.deleted_at.is_(None),
                        Rolls.deleted_at >= start_date
                    ),
                    Rolls.created_at >= start_date
                )
            )
            total_weight = (await session.execute(total_weight_query)).scalar_one_or_none()
            
            # Максимальный и минимальный промежуток между добавлением и удалением
            time_between_query = select(
                func.max((Rolls.deleted_at - Rolls.created_at)).label("max_time"),
                func.min((Rolls.deleted_at - Rolls.created_at)).label("min_time")
            ).where(
                and_(
                    Rolls.deleted_at.is_not(None),
                    Rolls.created_at <= end_date,
                    Rolls.deleted_at >= start_date
                )
            )
            time_between_result = (await session.execute(time_between_query)).one()

            max_time_between = time_between_result.max_time.total_seconds() / 86400 if time_between_result.max_time else None
            min_time_between = time_between_result.min_time.total_seconds() / 86400 if time_between_result.min_time else None

            # День с минимальным и максимальным количеством рулонов
            rolls_per_day_query = select(
                func.date(Rolls.created_at).label("day"),
                func.count().label("rolls_count")
            ).where(
                and_(
                    Rolls.created_at <= end_date,
                    or_(
                        Rolls.deleted_at.is_(None),
                        Rolls.deleted_at >= start_date
                    )
                )
            ).group_by(func.date(Rolls.created_at))
            
            rolls_per_day_result = (await session.execute(rolls_per_day_query)).all()

            if rolls_per_day_result:
                day_min_rolls = min(rolls_per_day_result, key=lambda x: x.rolls_count).day
                day_max_rolls = max(rolls_per_day_result, key=lambda x: x.rolls_count).day
            else:
                day_min_rolls = None
                day_max_rolls = None
            
            # День с минимальным и максимальным суммарным весом
            weight_per_day_query = select(
                func.date(Rolls.created_at).label("day"),
                func.sum(Rolls.weight).label("total_weight")
            ).where(
                and_(
                    Rolls.created_at <= end_date,
                    or_(
                        Rolls.deleted_at.is_(None),
                        Rolls.deleted_at >= start_date
                    )
                )
            ).group_by(func.date(Rolls.created_at))
            
            weight_per_day_result = (await session.execute(weight_per_day_query)).all()
            if weight_per_day_result:
                day_min_weight = min(weight_per_day_result, key=lambda x: x.total_weight).day
                day_max_weight = max(weight_per_day_result, key=lambda x: x.total_weight).day
            else:
                day_min_weight = None
                day_max_weight = None
            
            return {
                "total_added": total_added,
                "total_deleted": total_deleted,
                "avg_length": avg_length,
                "avg_weight": avg_weight,
                "max_length": max_length,
                "min_length": min_length,
                "max_weight": max_weight,
                "min_weight": min_weight,
                "total_weight": total_weight,
                "max_time_between_add_delete": max_time_between,  # в днях
                "min_time_between_add_delete": min_time_between,  # в днях
                "day_min_rolls": day_min_rolls,
                "day_max_rolls": day_max_rolls,
                "day_min_weight": day_min_weight,
                "day_max_weight": day_max_weight,
            }
