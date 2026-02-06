"""Add watchlist and portfolio tables

Revision ID: 7a8b9c1d2e3f
Revises: 6f06f1cbe0c7
Create Date: 2026-02-06 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '7a8b9c1d2e3f'
down_revision: Union[str, Sequence[str], None] = '6f06f1cbe0c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - add watchlist and portfolio tables."""

    # Create enums ONCE at the top (using postgresql.ENUM with create_type=True)
    alert_type_enum = postgresql.ENUM('SCORE_CHANGE', 'NEW_FLAGS', 'NEW_REPORT', name='alert_type_enum', create_type=True)
    alert_type_enum.create(op.get_bind(), checkfirst=True)

    alert_severity_enum = postgresql.ENUM('INFO', 'WARNING', 'CRITICAL', name='alert_severity_enum', create_type=True)
    alert_severity_enum.create(op.get_bind(), checkfirst=True)

    alert_frequency_enum = postgresql.ENUM('real_time', 'daily', 'weekly', 'none', name='alert_frequency_enum', create_type=True)
    alert_frequency_enum.create(op.get_bind(), checkfirst=True)

    # Create watchlist_items table
    op.create_table(
        'watchlist_items',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('company_id', sa.UUID(), nullable=False),
        sa.Column('added_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('alert_enabled', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('last_known_risk_score', sa.Integer(), nullable=True),
        sa.Column('last_checked_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'company_id', name='uq_user_company_watchlist')
    )
    op.create_index('idx_watchlist_user', 'watchlist_items', ['user_id'], unique=False)
    op.create_index('idx_watchlist_company', 'watchlist_items', ['company_id'], unique=False)

    # Create watchlist_alerts table
    op.create_table(
        'watchlist_alerts',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('watchlist_item_id', sa.UUID(), nullable=False),
        sa.Column('alert_type', postgresql.ENUM('SCORE_CHANGE', 'NEW_FLAGS', 'NEW_REPORT', name='alert_type_enum', create_type=False), nullable=False),
        sa.Column('severity', postgresql.ENUM('INFO', 'WARNING', 'CRITICAL', name='alert_severity_enum', create_type=False), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('previous_risk_score', sa.Integer(), nullable=True),
        sa.Column('current_risk_score', sa.Integer(), nullable=True),
        sa.Column('score_change', sa.Integer(), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['watchlist_item_id'], ['watchlist_items.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_alert_watchlist_item', 'watchlist_alerts', ['watchlist_item_id'], unique=False)
    op.create_index('idx_alert_read_status', 'watchlist_alerts', ['is_read'], unique=False)
    op.create_index('idx_alert_created', 'watchlist_alerts', ['created_at'], unique=False)

    # Create notification_preferences table
    op.create_table(
        'notification_preferences',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('email_alerts_enabled', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('weekly_digest_enabled', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('feature_announcements_enabled', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('push_notifications_enabled', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('push_subscription_endpoint', sa.String(length=512), nullable=True),
        sa.Column('push_subscription_keys', sa.Text(), nullable=True),
        sa.Column('alert_frequency', postgresql.ENUM('real_time', 'daily', 'weekly', 'none', name='alert_frequency_enum', create_type=False), nullable=False, server_default=sa.text("'real_time'")),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', name='uq_user_notification_prefs')
    )
    op.create_index('idx_notif_prefs_user', 'notification_preferences', ['user_id'], unique=True)

    # Create portfolios table
    op.create_table(
        'portfolios',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False, server_default=sa.text("'My Portfolio'")),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('total_investment', sa.Numeric(precision=15, scale=2), nullable=False, server_default=sa.text('0')),
        sa.Column('average_risk_score', sa.Float(), nullable=True),
        sa.Column('high_risk_count', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_portfolio_user', 'portfolios', ['user_id'], unique=False)

    # Create holdings table
    op.create_table(
        'holdings',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('portfolio_id', sa.UUID(), nullable=False),
        sa.Column('company_id', sa.UUID(), nullable=True),
        sa.Column('symbol', sa.String(length=50), nullable=False),
        sa.Column('company_name', sa.String(length=300), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('avg_price', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('investment_value', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('risk_score', sa.Integer(), nullable=True),
        sa.Column('risk_level', sa.String(length=20), nullable=True),
        sa.Column('flags_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['portfolio_id'], ['portfolios.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_holding_portfolio', 'holdings', ['portfolio_id'], unique=False)
    op.create_index('idx_holding_company', 'holdings', ['company_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema - remove watchlist and portfolio tables."""

    # Drop tables
    op.drop_index('idx_holding_company', table_name='holdings')
    op.drop_index('idx_holding_portfolio', table_name='holdings')
    op.drop_table('holdings')

    op.drop_index('idx_portfolio_user', table_name='portfolios')
    op.drop_table('portfolios')

    op.drop_index('idx_notif_prefs_user', table_name='notification_preferences')
    op.drop_table('notification_preferences')

    op.drop_index('idx_alert_created', table_name='watchlist_alerts')
    op.drop_index('idx_alert_read_status', table_name='watchlist_alerts')
    op.drop_index('idx_alert_watchlist_item', table_name='watchlist_alerts')
    op.drop_table('watchlist_alerts')

    op.drop_index('idx_watchlist_company', table_name='watchlist_items')
    op.drop_index('idx_watchlist_user', table_name='watchlist_items')
    op.drop_table('watchlist_items')

    # Drop enums
    sa.Enum(name='alert_frequency_enum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='alert_severity_enum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='alert_type_enum').drop(op.get_bind(), checkfirst=True)
