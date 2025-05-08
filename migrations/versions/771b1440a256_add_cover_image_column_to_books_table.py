"""Add cover_image column to books table

Revision ID: 771b1440a256
Revises: de6fe44266a2
Create Date: 2024-11-28 12:40:57.640531

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '771b1440a256'
down_revision = 'de6fe44266a2'
branch_labels = None
depends_on = None


def upgrade():
    # Use raw SQL to check if the `cover_image` column exists
    conn = op.get_bind()
    result = conn.execute(
        sa.text("SHOW COLUMNS FROM books LIKE 'cover_image';")
    )
    column_exists = result.fetchone() is not None

    # Add the `cover_image` column if it doesn't exist
    if not column_exists:
        with op.batch_alter_table('books', schema=None) as batch_op:
            batch_op.add_column(sa.Column('cover_image', mysql.LONGBLOB(), nullable=True))

    # Recreate the foreign key constraint to ensure integrity
    with op.batch_alter_table('borrowed_books', schema=None) as batch_op:
        batch_op.drop_constraint('fk_borrowed_books_book_title_books', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_borrowed_books_book_title_books',
            'books',
            ['book_title'],
            ['title'],
            ondelete='CASCADE'
        )


def downgrade():
    # Remove the `cover_image` column
    with op.batch_alter_table('books', schema=None) as batch_op:
        batch_op.drop_column('cover_image')

    # Recreate the original foreign key constraint
    with op.batch_alter_table('borrowed_books', schema=None) as batch_op:
        batch_op.drop_constraint('fk_borrowed_books_book_title_books', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_borrowed_books_book_title_books',
            'books',
            ['book_title'],
            ['title']
        )
