from sqlalchemy import TIMESTAMP, CheckConstraint, Column, Integer, Numeric,func

from app.database import Base


class Rolls(Base):
    __tablename__ = "rolls"

    id = Column(Integer, primary_key=True, index=True)
    length = Column(Numeric(10, 2), nullable=False)
    weight = Column(Numeric(10, 2), nullable=False) 
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    deleted_at = Column(TIMESTAMP, nullable=True) 


    __table_args__ = (
        CheckConstraint('length >= 0', name='check_length_positive'),
        CheckConstraint('weight >= 0', name='check_weight_positive'),
    )