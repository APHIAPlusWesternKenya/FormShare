"""Update mime type size

Revision ID: 3932ad37cc0b
Revises: 2e67eb119c02
Create Date: 2019-11-27 09:57:25.577630

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "3932ad37cc0b"
down_revision = "2e67eb119c02"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "mediafile",
        "file_mimetype",
        existing_type=sa.Unicode(length=64),
        type_=sa.Unicode(length=120),
        existing_nullable=True,
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "mediafile",
        "file_mimetype",
        existing_type=sa.Unicode(length=120),
        type_=sa.Unicode(length=64),
        existing_nullable=True,
    )
    # ### end Alembic commands ###