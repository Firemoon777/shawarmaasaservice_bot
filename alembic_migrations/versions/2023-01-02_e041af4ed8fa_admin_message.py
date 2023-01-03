"""admin_message

Revision ID: e041af4ed8fa
Revises: d7cc6c5443aa
Create Date: 2023-01-02 18:39:06.753826

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e041af4ed8fa'
down_revision = 'd7cc6c5443aa'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shaas_event', sa.Column('admin_message_id', sa.BigInteger(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('shaas_event', 'admin_message_id')
    # ### end Alembic commands ###
