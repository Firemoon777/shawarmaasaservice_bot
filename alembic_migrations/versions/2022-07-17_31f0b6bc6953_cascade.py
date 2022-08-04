"""cascade

Revision ID: 31f0b6bc6953
Revises: cb124d002ea3
Create Date: 2022-07-17 16:35:56.583676

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '31f0b6bc6953'
down_revision = 'cb124d002ea3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('shaas_order_entry_order_id_fkey', 'shaas_order_entry', type_='foreignkey')
    op.create_foreign_key(None, 'shaas_order_entry', 'shaas_order', ['order_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'shaas_order_entry', type_='foreignkey')
    op.create_foreign_key('shaas_order_entry_order_id_fkey', 'shaas_order_entry', 'shaas_order', ['order_id'], ['id'])
    # ### end Alembic commands ###