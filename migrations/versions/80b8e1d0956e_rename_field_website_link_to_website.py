"""Rename field  website_link to website

Revision ID: 80b8e1d0956e
Revises: 71f474b5f1d8
Create Date: 2022-08-17 19:13:57.074453

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '80b8e1d0956e'
down_revision = '71f474b5f1d8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('website', sa.String(length=120), nullable=True))
    op.drop_column('Artist', 'website_link')
    op.add_column('Venue', sa.Column('website', sa.String(length=120), nullable=True))
    op.drop_column('Venue', 'website_link')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('website_link', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.drop_column('Venue', 'website')
    op.add_column('Artist', sa.Column('website_link', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.drop_column('Artist', 'website')
    # ### end Alembic commands ###
