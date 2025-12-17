"""remove barcode unique constraint

Revision ID: a1b2c3d4e5f6
Revises: 8501834e4079
Create Date: 2025-12-17 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '8501834e4079'  # Son migration'ın revision ID'si
branch_labels = None
depends_on = None


def upgrade():
    # Barcode unique constraint'ini kaldır
    # SQLite için batch_alter_table kullan
    try:
        with op.batch_alter_table('book', schema=None) as batch_op:
            # Önce unique index'i kaldır
            batch_op.drop_index('ix_book_barcode', if_exists=True)
            # Sonra column'u unique olmayacak şekilde güncelle
            batch_op.alter_column('barcode',
                               existing_type=sa.String(length=12),
                               nullable=False,
                               unique=False)
    except Exception as e:
        # MySQL veya PostgreSQL için
        try:
            op.drop_index('ix_book_barcode', table_name='book')
        except:
            pass
        try:
            op.drop_index('barcode', table_name='book')
        except:
            pass


def downgrade():
    # Geri alma işlemi (unique constraint'i geri ekle)
    try:
        with op.batch_alter_table('book', schema=None) as batch_op:
            batch_op.create_unique_constraint('ix_book_barcode', ['barcode'])
    except:
        try:
            op.create_index('ix_book_barcode', 'book', ['barcode'], unique=True)
        except:
            pass

