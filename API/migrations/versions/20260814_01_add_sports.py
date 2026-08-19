"""Add sports tournaments.

Revision ID: 20260814_01
Revises:
Create Date: 2026-08-14
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260814_01"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

sport_type = sa.Enum("football", "volleyball", "basketball", name="sporttype")
season_phase = sa.Enum("setup", "group_stage", "knockout", "completed", name="sportsseasonphase")
match_stage = sa.Enum("group", "quarterfinal", "semifinal", "third_place", "final", name="sportsmatchstage")
match_status = sa.Enum("scheduled", "postponed", "completed", "forfeited", name="sportsmatchstatus")
group_type = sa.Enum("A", "B", "C", "D", name="sportsgroup")


def upgrade() -> None:
    op.create_table(
        "sports_seasons",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sport", sport_type, nullable=False),
        sa.Column("school_year", sa.String(length=7), nullable=False),
        sa.Column("phase", season_phase, nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("updated", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("sport", "school_year", name="uq_sports_season"),
    )
    op.create_index("ix_sports_seasons_sport", "sports_seasons", ["sport"])
    op.create_index("ix_sports_seasons_school_year", "sports_seasons", ["school_year"])

    op.create_table(
        "sports_rules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "season_id", sa.Integer(), sa.ForeignKey("sports_seasons.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("position", sa.SmallInteger(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("url", sa.Text(), nullable=True),
        sa.UniqueConstraint("season_id", "position", name="uq_sports_rule_position"),
    )
    op.create_index("ix_sports_rules_season_id", "sports_rules", ["season_id"])

    op.create_table(
        "sports_participants",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "season_id", sa.Integer(), sa.ForeignKey("sports_seasons.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("class_code", sa.String(length=2), nullable=False),
        sa.Column("group", group_type, nullable=False),
        sa.Column("qualified_rank", sa.SmallInteger(), nullable=True),
        sa.UniqueConstraint("season_id", "class_code", name="uq_sports_participant"),
    )
    op.create_index("ix_sports_participants_season_id", "sports_participants", ["season_id"])
    op.create_index("ix_sports_participants_group", "sports_participants", ["group"])

    op.create_table(
        "sports_matches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "season_id", sa.Integer(), sa.ForeignKey("sports_seasons.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("stage", match_stage, nullable=False),
        sa.Column("status", match_status, nullable=False),
        sa.Column("group", group_type, nullable=True),
        sa.Column("bracket_slot", sa.String(length=8), nullable=True),
        sa.Column("date", sa.Date(), nullable=True),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column(
            "home_participant_id",
            sa.Integer(),
            sa.ForeignKey("sports_participants.id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.Column(
            "away_participant_id",
            sa.Integer(),
            sa.ForeignKey("sports_participants.id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.Column("home_score", sa.Integer(), nullable=True),
        sa.Column("away_score", sa.Integer(), nullable=True),
        sa.Column("home_penalties", sa.Integer(), nullable=True),
        sa.Column("away_penalties", sa.Integer(), nullable=True),
        sa.Column(
            "forfeit_winner_id",
            sa.Integer(),
            sa.ForeignKey("sports_participants.id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("updated", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("season_id", "bracket_slot", name="uq_sports_bracket_slot"),
    )
    for column in (
        "season_id",
        "stage",
        "group",
        "date",
        "home_participant_id",
        "away_participant_id",
        "forfeit_winner_id",
    ):
        op.create_index(f"ix_sports_matches_{column}", "sports_matches", [column])
    op.create_index("ix_sports_matches_date_status", "sports_matches", ["date", "status"])

    op.create_table(
        "volleyball_set_scores",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "match_id", sa.Integer(), sa.ForeignKey("sports_matches.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("set_number", sa.SmallInteger(), nullable=False),
        sa.Column("home_score", sa.Integer(), nullable=False),
        sa.Column("away_score", sa.Integer(), nullable=False),
        sa.UniqueConstraint("match_id", "set_number", name="uq_volleyball_match_set"),
    )
    op.create_index("ix_volleyball_set_scores_match_id", "volleyball_set_scores", ["match_id"])

    op.create_table(
        "sports_qualification_decisions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "season_id", sa.Integer(), sa.ForeignKey("sports_seasons.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("group", group_type, nullable=False),
        sa.Column("ordered_classes_json", sa.Text(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.UniqueConstraint("season_id", "group", name="uq_sports_qualification_group"),
    )
    op.create_index(
        "ix_sports_qualification_decisions_season_id", "sports_qualification_decisions", ["season_id"]
    )

    op.create_table(
        "sports_audit_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sport", sport_type, nullable=False),
        sa.Column("school_year", sa.String(length=7), nullable=False),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("record_type", sa.String(length=80), nullable=False),
        sa.Column("record_id", sa.Integer(), nullable=True),
        sa.Column("before_json", sa.Text(length=70000), nullable=True),
        sa.Column("after_json", sa.Text(length=70000), nullable=True),
        sa.Column("created", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_sports_audit_entries_sport", "sports_audit_entries", ["sport"])
    op.create_index("ix_sports_audit_entries_school_year", "sports_audit_entries", ["school_year"])
    op.create_index("ix_sports_audit_entries_created", "sports_audit_entries", ["created"])


def downgrade() -> None:
    op.drop_table("sports_audit_entries")
    op.drop_table("sports_qualification_decisions")
    op.drop_table("volleyball_set_scores")
    op.drop_table("sports_matches")
    op.drop_table("sports_participants")
    op.drop_table("sports_rules")
    op.drop_table("sports_seasons")
