from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class RollCreate(BaseModel):
    length: float = Field(gt=0)
    weight: float = Field(gt=0)

class RollResponse(BaseModel):
    id: int
    length: float
    weight: float
    created_at: datetime
    deleted_at: datetime | None

    class ConfigDict:
        model_config = ConfigDict(from_attributes=True)

class RollFilter(BaseModel):
    id_min: int | None = Field(None, description="Минимальное значение id")
    id_max: int | None = Field(None, description="Максимальное значение id")
    weight_min: float | None = Field(None, description="Минимальный вес")
    weight_max: float | None = Field(None, description="Максимальный вес")
    length_min: float | None = Field(None, description="Минимальная длина")
    length_max: float | None = Field(None, description="Максимальная длина")
    created_at_min: datetime | None = Field(None, description="Минимальная дата добавления")
    created_at_max: datetime | None = Field(None, description="Максимальная дата добавления")
    deleted_at_min: datetime | None = Field(None, description="Минимальная дата удаления")
    deleted_at_max: datetime | None = Field(None, description="Максимальная дата удаления")

class RollStatisticsResponse(BaseModel):
    total_added: int
    total_deleted: int
    avg_length: float | None
    avg_weight: float | None
    max_length: float | None
    min_length: float | None
    max_weight: float | None
    min_weight: float | None
    total_weight: float | None
    max_time_between_add_delete: float | None
    min_time_between_add_delete: float | None 
    day_min_rolls: date | None
    day_max_rolls: date | None
    day_min_weight: date | None
    day_max_weight: date | None