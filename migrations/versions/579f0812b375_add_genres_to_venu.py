"""Add genres to Venu

Revision ID: 579f0812b375
Revises: 80b8e1d0956e
Create Date: 2022-08-17 20:18:48.254674

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '579f0812b375'
down_revision = '80b8e1d0956e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('genres', sa.ARRAY(sa.String()), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'genres')
    # ### end Alembic commands ###
