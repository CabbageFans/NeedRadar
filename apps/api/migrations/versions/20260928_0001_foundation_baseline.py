"""empty Foundation baseline

Revision ID: 20260928_0001
Revises: None
Create Date: 2026-09-28 00:00:00+08:00
"""

from collections.abc import Sequence

revision: str = "20260928_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Establish Alembic authority without any business table."""


def downgrade() -> None:
    """Return to base; there is no business schema to remove."""
