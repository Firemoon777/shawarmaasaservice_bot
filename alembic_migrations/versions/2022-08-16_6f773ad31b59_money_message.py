"""money_message

Revision ID: 6f773ad31b59
Revises: ec5ffc6fcee4
Create Date: 2022-08-16 18:19:18.054808

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6f773ad31b59'
down_revision = 'ec5ffc6fcee4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shaas_event', sa.Column('money_message', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('shaas_event', 'money_message')
    # ### end Alembic commands ###
