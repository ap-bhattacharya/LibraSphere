"""Update BorrowedBook model relationships

Revision ID: de6fe44266a2
Revises: a271c51f187c
Create Date: 2024-11-28 10:37:16.361655

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'de6fe44266a2'
down_revision = 'a271c51f187c'
branch_labels = None
depends_on = None


def upgrade():
    # Ensure `book_title` column is not nullable
    with op.batch_alter_table('borrowed_books', schema=None) as batch_op:
        batch_op.alter_column(
            'book_title',
            existing_type=mysql.VARCHAR(length=255),
            nullable=False
        )
        batch_op.alter_column(
            'borrowed_by_user',
            existing_type=mysql.VARCHAR(length=255),
            nullable=False
        )


def downgrade():
    # Reverse column alterations to make them nullable
    with op.batch_alter_table('borrowed_books', schema=None) as batch_op:
        batch_op.alter_column(
            'book_title',
            existing_type=mysql.VARCHAR(length=255),
            nullable=True
        )
        batch_op.alter_column(
            'borrowed_by_user',
            existing_type=mysql.VARCHAR(length=255),
            nullable=True
        )
