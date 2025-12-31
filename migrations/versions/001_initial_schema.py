# ============================================================================
# migrations/versions/001_initial_schema.py - Initial Database Schema
# ============================================================================

"""Initial schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()'), onupdate=sa.text('NOW()')),
        sa.Column('last_login', sa.TIMESTAMP(timezone=True)),
        sa.Column('email_verified', sa.Boolean, default=False),
        sa.Column('metadata', postgresql.JSONB, server_default=sa.text("'{}'::jsonb"))
    )
    
    # Create indexes for users
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_created_at', 'users', ['created_at'])
    
    # Create sessions table
    op.create_table(
        'sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('refresh_token', sa.String(500), nullable=False, unique=True),
        sa.Column('device_info', postgresql.JSONB),
        sa.Column('ip_address', postgresql.INET),
        sa.Column('user_agent', sa.Text),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('last_used_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('expires_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('revoked', sa.Boolean, default=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    
    # Create indexes for sessions
    op.create_index('idx_sessions_user_id', 'sessions', ['user_id'])
    op.create_index('idx_sessions_refresh_token', 'sessions', ['refresh_token'])
    op.create_index('idx_sessions_expires_at', 'sessions', ['expires_at'])
    
    # Create executions table
    op.create_table(
        'executions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('input_type', sa.String(50), nullable=False),
        sa.Column('input_value', sa.Text, nullable=False),
        sa.Column('input_file_url', sa.Text),
        sa.Column('status', sa.String(50), nullable=False, server_default='planned'),
        sa.Column('plan', postgresql.JSONB),
        sa.Column('current_step', sa.Integer, default=0),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('started_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('completed_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('metadata', postgresql.JSONB, server_default=sa.text("'{}'::jsonb")),
        sa.Column('error_message', sa.Text),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    
    # Create indexes for executions
    op.create_index('idx_executions_user_id', 'executions', ['user_id'])
    op.create_index('idx_executions_status', 'executions', ['status'])
    op.create_index('idx_executions_created_at', 'executions', ['created_at'])
    op.create_index('idx_executions_user_status', 'executions', ['user_id', 'status'])
    
    # Create execution_logs table
    op.create_table(
        'execution_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('execution_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('timestamp', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('level', sa.String(20), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('metadata', postgresql.JSONB),
        sa.Column('step_id', sa.Integer),
        sa.ForeignKeyConstraint(['execution_id'], ['executions.id'], ondelete='CASCADE')
    )
    
    # Create indexes for execution_logs
    op.create_index('idx_execution_logs_execution_id', 'execution_logs', ['execution_id'])
    op.create_index('idx_execution_logs_timestamp', 'execution_logs', ['timestamp'])
    
    # Create artifacts table
    op.create_table(
        'artifacts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('execution_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('name', sa.String(255)),
        sa.Column('data', postgresql.JSONB),
        sa.Column('file_url', sa.Text),
        sa.Column('file_size_bytes', sa.BigInteger),
        sa.Column('mime_type', sa.String(100)),
        sa.Column('verified', sa.Boolean, default=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['execution_id'], ['executions.id'], ondelete='CASCADE')
    )
    
    # Create indexes for artifacts
    op.create_index('idx_artifacts_execution_id', 'artifacts', ['execution_id'])
    op.create_index('idx_artifacts_type', 'artifacts', ['type'])
    
    # Create trigger function for updated_at
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
    
    # Create trigger for users table
    op.execute("""
        CREATE TRIGGER update_users_updated_at
            BEFORE UPDATE ON users
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    # Drop triggers
    op.execute('DROP TRIGGER IF EXISTS update_users_updated_at ON users')
    op.execute('DROP FUNCTION IF EXISTS update_updated_at_column()')
    
    # Drop tables in reverse order
    op.drop_table('artifacts')
    op.drop_table('execution_logs')
    op.drop_table('executions')
    op.drop_table('sessions')
    op.drop_table('users')
    
    # Drop extensions
    op.execute('DROP EXTENSION IF EXISTS "pgcrypto"')
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
