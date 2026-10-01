"""Create the analytics event store for the observed VARCHAR user schema.

Revision ID: sr_analytics_001
Revises:
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "sr_analytics_001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create only the analytics table after validating the existing user key."""
    op.execute("""
        DO $validate_legacy_users$
        DECLARE
            id_type text;
            id_length integer;
            has_expected_primary_key boolean;
        BEGIN
            SELECT data_type, character_maximum_length
              INTO id_type, id_length
              FROM information_schema.columns
             WHERE table_schema = 'public'
               AND table_name = 'users'
               AND column_name = 'id';

            IF id_type IS DISTINCT FROM 'character varying' OR id_length IS DISTINCT FROM 36 THEN
                RAISE EXCEPTION 'Analytics migration requires public.users.id VARCHAR(36); found type %, length %', id_type, id_length;
            END IF;

            SELECT EXISTS (
                SELECT 1
                  FROM pg_catalog.pg_constraint c
                  JOIN pg_catalog.pg_attribute a
                    ON a.attrelid = c.conrelid AND a.attnum = c.conkey[1]
                 WHERE c.conrelid = 'public.users'::regclass
                   AND c.contype = 'p'
                   AND cardinality(c.conkey) = 1
                   AND a.attname = 'id'
            ) INTO has_expected_primary_key;

            IF NOT has_expected_primary_key THEN
                RAISE EXCEPTION 'Analytics migration requires public.users.id to be the sole primary key';
            END IF;

            IF EXISTS (
                SELECT 1 FROM pg_catalog.pg_tables
                 WHERE tablename = 'analytics_events'
            ) THEN
                RAISE EXCEPTION 'analytics_events already exists; inspect it before adopting this migration';
            END IF;
        END;
        $validate_legacy_users$;
        """)

    op.create_table(
        "analytics_events",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("event_name", sa.String(255), nullable=False),
        sa.Column("source", sa.String(100), nullable=False),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("public.users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("session_id", sa.String(100)),
        sa.Column("correlation_id", sa.String(64)),
        sa.Column(
            "properties",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("numeric_value", sa.DECIMAL(20, 6)),
        sa.Column("string_value", sa.String(500)),
        sa.Column("ip_address", sa.String(45)),
        sa.Column("user_agent", sa.String(500)),
        sa.Column("geo_country", sa.String(2)),
        sa.Column("geo_region", sa.String(100)),
        sa.Column(
            "event_timestamp",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="public",
    )

    op.create_index(
        "ix_analytics_events_event_type", "analytics_events", ["event_type"], schema="public"
    )
    op.create_index(
        "ix_analytics_events_event_name", "analytics_events", ["event_name"], schema="public"
    )
    op.create_index("ix_analytics_events_source", "analytics_events", ["source"], schema="public")
    op.create_index("ix_analytics_events_user_id", "analytics_events", ["user_id"], schema="public")
    op.create_index(
        "ix_analytics_events_session_id", "analytics_events", ["session_id"], schema="public"
    )
    op.create_index(
        "ix_analytics_events_correlation_id",
        "analytics_events",
        ["correlation_id"],
        schema="public",
    )
    op.create_index(
        "ix_analytics_events_event_timestamp",
        "analytics_events",
        ["event_timestamp"],
        schema="public",
    )
    op.create_index(
        "ix_analytics_events_type_timestamp",
        "analytics_events",
        ["event_type", "event_timestamp"],
        schema="public",
    )


def downgrade() -> None:
    """Refuse to remove recorded events; empty-table rollback leaves users intact."""
    # Alembic's transactional DDL retains this lock through the empty check,
    # drops, and version update; concurrent writers cannot enter the gap.
    op.execute("SET LOCAL lock_timeout = '5s'")
    op.execute("LOCK TABLE public.analytics_events IN ACCESS EXCLUSIVE MODE")
    op.execute("""
        DO $protect_analytics_data$
        BEGIN
            IF EXISTS (SELECT 1 FROM public.analytics_events LIMIT 1) THEN
                RAISE EXCEPTION 'Refusing to drop analytics_events while recorded data exists';
            END IF;
        END;
        $protect_analytics_data$;
        """)
    op.drop_index(
        "ix_analytics_events_type_timestamp", table_name="analytics_events", schema="public"
    )
    op.drop_index(
        "ix_analytics_events_event_timestamp", table_name="analytics_events", schema="public"
    )
    op.drop_index(
        "ix_analytics_events_correlation_id", table_name="analytics_events", schema="public"
    )
    op.drop_index("ix_analytics_events_session_id", table_name="analytics_events", schema="public")
    op.drop_index("ix_analytics_events_user_id", table_name="analytics_events", schema="public")
    op.drop_index("ix_analytics_events_source", table_name="analytics_events", schema="public")
    op.drop_index("ix_analytics_events_event_name", table_name="analytics_events", schema="public")
    op.drop_index("ix_analytics_events_event_type", table_name="analytics_events", schema="public")
    op.drop_table("analytics_events", schema="public")
