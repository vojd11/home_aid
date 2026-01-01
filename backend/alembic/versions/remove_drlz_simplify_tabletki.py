"""remove drlz fields and simplify tabletki

Revision ID: remove_drlz_simplify_tabletki
Revises: 1238702f085a
Create Date: 2024-08-24 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'remove_drlz_simplify_tabletki'
down_revision = '1238702f085a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if columns exist before dropping them
    from alembic import context
    from sqlalchemy import text
    connection = context.get_bind()
    
    # Check if drlz_link column exists
    result = connection.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'medications' AND column_name = 'drlz_link'
    """))
    if result.fetchone():
        op.drop_column('medications', 'drlz_link')
    
    # Check if drlz_instruction_link column exists
    result = connection.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'medications' AND column_name = 'drlz_instruction_link'
    """))
    if result.fetchone():
        op.drop_column('medications', 'drlz_instruction_link')
    
    # Update external_resolutions table to remove DRLZ-related fields
    op.execute("DELETE FROM external_resolutions WHERE source = 'DRLZ'")


def downgrade() -> None:
    # Add back DRLZ columns
    op.add_column('medications', sa.Column('drlz_link', sa.Text(), nullable=True))
    op.add_column('medications', sa.Column('drlz_instruction_link', sa.Text(), nullable=True))
