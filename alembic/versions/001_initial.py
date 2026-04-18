"""Initial migration

Revision ID: 001_initial
Revises: 
Create Date: 2026-04-18

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user_preferences table
    op.create_table(
        'user_preferences',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('topic', sa.String(), nullable=False),
        sa.Column('tone', postgresql.ENUM('FORMAL', 'INFORMAL', 'SARCASTIC', 'ELI5', name='tone'), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    
    # Create briefings table
    op.create_table(
        'briefings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('status', postgresql.ENUM('PENDING', 'COMPLETED', 'FAILED', name='briefingstatus'), nullable=False),
        sa.Column('items', postgresql.JSON(), server_default='[]'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('briefings')
    op.drop_table('user_preferences')
    op.execute("DROP TYPE IF EXISTS tone")
    op.execute("DROP TYPE IF EXISTS briefingstatus")