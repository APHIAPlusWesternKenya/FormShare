"""Add hex-color to form

Revision ID: 1681ed03029c
Revises: 19649c355612
Create Date: 2019-03-04 10:05:20.898852

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1681ed03029c'
down_revision = '19649c355612'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('odkform', sa.Column('form_hexcolor', sa.Unicode(length=60), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('odkform', 'form_hexcolor')
    # ### end Alembic commands ###