"""Make drive_file_id non-nullable

Revision ID: 15517478426d
Revises: 605fa91c7af5
Create Date: 2024-09-29 01:55:36.484890

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '15517478426d'
down_revision = '605fa91c7af5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('upload_music',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('filename', sa.String(length=256), nullable=False),
    sa.Column('uploader_username', sa.String(length=64), nullable=False),
    sa.Column('drive_file_id', sa.String(length=256), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('upload_music')
    # ### end Alembic commands ###
