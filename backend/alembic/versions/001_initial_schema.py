"""001_initial_schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-11-23 03:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'user_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('token_hash', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_activity_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_user_sessions_token_hash', 'user_sessions', ['token_hash'], unique=True)

    op.create_table(
        'user_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('preferred_language', sa.String(length=10), nullable=False, server_default='en'),
        sa.Column('household_preferences', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('commuting_preferences', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('indoor_environment_preferences', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('sensitive_group_consent', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['user_sessions.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_user_profiles_session_id', 'user_profiles', ['session_id'], unique=True)

    op.create_table(
        'saved_locations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('region', sa.String(length=100), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['user_sessions.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_saved_locations_session_id', 'saved_locations', ['session_id'], unique=False)

    op.create_table(
        'air_quality_snapshots',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False, server_default='Open-Meteo'),
        sa.Column('index_standard', sa.String(length=20), nullable=False, server_default='US_AQI'),
        sa.Column('aqi_value', sa.Integer(), nullable=False),
        sa.Column('aqi_category', sa.String(length=50), nullable=False),
        sa.Column('pollutant_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('source_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('observed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_air_quality_coords', 'air_quality_snapshots', ['latitude', 'longitude'], unique=False)
    op.create_index('ix_air_quality_snapshots_expires_at', 'air_quality_snapshots', ['expires_at'], unique=False)

    op.create_table(
        'recommendation_plans',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('location_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('source_snapshot_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('ai_model', sa.String(length=50), nullable=False, server_default='openai/gpt-oss-120b'),
        sa.Column('recommendation_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['user_sessions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['location_id'], ['saved_locations.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['source_snapshot_id'], ['air_quality_snapshots.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_recommendation_plans_session_id', 'recommendation_plans', ['session_id'], unique=False)

    op.create_table(
        'user_feedback',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('recommendation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint('rating >= 1 AND rating <= 5', name='ck_feedback_rating_range'),
        sa.ForeignKeyConstraint(['session_id'], ['user_sessions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['recommendation_id'], ['recommendation_plans.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_user_feedback_session_id', 'user_feedback', ['session_id'], unique=False)
    op.create_index('ix_user_feedback_recommendation_id', 'user_feedback', ['recommendation_id'], unique=False)


def downgrade() -> None:
    op.drop_table('user_feedback')
    op.drop_table('recommendation_plans')
    op.drop_table('air_quality_snapshots')
    op.drop_table('saved_locations')
    op.drop_table('user_profiles')
    op.drop_table('user_sessions')
