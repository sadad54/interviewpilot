"""Add stateful agentic interview workflow.

Revision ID: 20260718_0001
"""
from alembic import op
import sqlalchemy as sa
import uuid

revision = "20260718_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    tables = set(sa.inspect(bind).get_table_names())
    if "interview_sessions" not in tables:
        from app.core.database import Base
        from app import models  # noqa: F401
        Base.metadata.create_all(bind)
        return

    with op.batch_alter_table("interview_sessions") as batch:
        batch.add_column(sa.Column("public_id", sa.String(36), nullable=True))
        batch.add_column(sa.Column("seniority", sa.String(), nullable=False, server_default="mid"))
        batch.add_column(sa.Column("job_description", sa.Text(), nullable=True))
        batch.add_column(sa.Column("current_question_id", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("primary_question_count", sa.Integer(), nullable=False, server_default="5"))
        batch.add_column(sa.Column("current_primary_index", sa.Integer(), nullable=False, server_default="0"))
        batch.add_column(sa.Column("version", sa.Integer(), nullable=False, server_default="1"))
        batch.add_column(sa.Column("plan_summary", sa.JSON(), nullable=False, server_default="{}"))
        batch.add_column(sa.Column("started_at", sa.DateTime(timezone=True), nullable=True))
        batch.add_column(sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True))
        batch.create_foreign_key("fk_session_current_question", "questions", ["current_question_id"], ["id"])
    session_ids = bind.execute(sa.text("SELECT id FROM interview_sessions WHERE public_id IS NULL")).scalars().all()
    for session_id in session_ids:
        bind.execute(
            sa.text("UPDATE interview_sessions SET public_id = :public_id WHERE id = :session_id"),
            {"public_id": str(uuid.uuid4()), "session_id": session_id},
        )
    with op.batch_alter_table("interview_sessions") as batch:
        batch.alter_column("public_id", nullable=False)
        batch.create_unique_constraint("uq_interview_sessions_public_id", ["public_id"])

    with op.batch_alter_table("questions") as batch:
        batch.add_column(sa.Column("is_template", sa.Boolean(), nullable=False, server_default=sa.true()))
        batch.add_column(sa.Column("session_id", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("template_id", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("parent_question_id", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("kind", sa.String(), nullable=False, server_default="primary"))
        batch.add_column(sa.Column("competency", sa.String(), nullable=False, server_default="technical_depth"))
        batch.add_column(sa.Column("sequence_index", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("planner_metadata", sa.JSON(), nullable=False, server_default="{}"))
        batch.create_foreign_key("fk_question_session", "interview_sessions", ["session_id"], ["id"])
        batch.create_foreign_key("fk_question_template", "questions", ["template_id"], ["id"])
        batch.create_foreign_key("fk_question_parent", "questions", ["parent_question_id"], ["id"])

    with op.batch_alter_table("responses") as batch:
        batch.add_column(sa.Column("client_request_id", sa.String(64), nullable=True))
        batch.add_column(sa.Column("answer_mode", sa.String(16), nullable=False, server_default="text"))
        batch.create_unique_constraint("uq_responses_client_request_id", ["client_request_id"])

    with op.batch_alter_table("evaluations") as batch:
        batch.add_column(sa.Column("next_action", sa.Text(), nullable=True))
        batch.add_column(sa.Column("strengths", sa.JSON(), nullable=False, server_default="[]"))
        batch.add_column(sa.Column("gaps", sa.JSON(), nullable=False, server_default="[]"))
        batch.add_column(sa.Column("confidence", sa.Float(), nullable=True))
        batch.add_column(sa.Column("decision_summary", sa.Text(), nullable=True))

    if "session_reports" not in tables:
        op.create_table(
            "session_reports",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("session_id", sa.Integer(), sa.ForeignKey("interview_sessions.id"), nullable=False, unique=True),
            sa.Column("share_token", sa.String(48), nullable=False, unique=True),
            sa.Column("overall_score", sa.Float(), nullable=False),
            sa.Column("competency_scores", sa.JSON(), nullable=False),
            sa.Column("strengths", sa.JSON(), nullable=False),
            sa.Column("improvements", sa.JSON(), nullable=False),
            sa.Column("summary", sa.Text(), nullable=False),
            sa.Column("evidence", sa.JSON(), nullable=False),
            sa.Column("coverage_summary", sa.JSON(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
        )


def downgrade():
    op.drop_table("session_reports")
    with op.batch_alter_table("evaluations") as batch:
        for name in ["decision_summary", "confidence", "gaps", "strengths", "next_action"]:
            batch.drop_column(name)
    with op.batch_alter_table("responses") as batch:
        batch.drop_constraint("uq_responses_client_request_id", type_="unique")
        batch.drop_column("answer_mode")
        batch.drop_column("client_request_id")
    with op.batch_alter_table("questions") as batch:
        for name in ["planner_metadata", "sequence_index", "competency", "kind", "parent_question_id", "template_id", "session_id", "is_template"]:
            batch.drop_column(name)
    with op.batch_alter_table("interview_sessions") as batch:
        batch.drop_constraint("uq_interview_sessions_public_id", type_="unique")
        for name in ["completed_at", "started_at", "plan_summary", "version", "current_primary_index", "primary_question_count", "current_question_id", "job_description", "seniority", "public_id"]:
            batch.drop_column(name)
