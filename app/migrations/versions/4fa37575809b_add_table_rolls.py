"""add table rolls

Revision ID: 4fa37575809b
Revises: 
Create Date: 2025-03-20 19:49:05.635841

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '4fa37575809b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('rolls',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('length', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('weight', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
    sa.CheckConstraint('length >= 0', name='check_length_positive'),
    sa.CheckConstraint('weight >= 0', name='check_weight_positive'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rolls_id'), 'rolls', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_rolls_id'), table_name='rolls')
    op.drop_table('rolls')
    # ### end Alembic commands ###
