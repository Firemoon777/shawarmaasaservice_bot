"""deprecated poll

Revision ID: ec5ffc6fcee4
Revises: 35da919ac385
Create Date: 2022-08-04 14:57:15.684992

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ec5ffc6fcee4'
down_revision = '35da919ac385'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shaas_event', sa.Column('order_message_id', sa.BigInteger(), nullable=True))
    op.add_column('shaas_event', sa.Column('additional_message_id', sa.BigInteger(), nullable=True))
    op.alter_column('shaas_event', 'poll_message_id',
               existing_type=sa.BIGINT(),
               nullable=True)
    op.alter_column('shaas_event', 'poll_id',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('shaas_event', 'skip_option',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('shaas_event', 'skip_option',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('shaas_event', 'poll_id',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('shaas_event', 'poll_message_id',
               existing_type=sa.BIGINT(),
               nullable=False)
    op.drop_column('shaas_event', 'additional_message_id')
    op.drop_column('shaas_event', 'order_message_id')
    # ### end Alembic commands ###
