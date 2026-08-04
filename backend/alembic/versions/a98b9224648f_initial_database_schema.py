"""initial database schema

Revision ID: a98b9224648f
Revises: 029a2dc11b69
Create Date: 2026-08-04 10:37:48.346707

"""
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'a98b9224648f'
down_revision: str | Sequence[str] | None = '029a2dc11b69'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('predictions') as batch_op:
        batch_op.drop_constraint(op.f('uq_predictions_prediction_model_snapshot_horizon'), type_='unique')
        batch_op.create_unique_constraint('prediction_model_snapshot_horizon', ['repository_snapshot_id', 'model_version_id', 'prediction_horizon_days'])


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('predictions') as batch_op:
        batch_op.drop_constraint('prediction_model_snapshot_horizon', type_='unique')
        batch_op.create_unique_constraint(op.f('uq_predictions_prediction_model_snapshot_horizon'), ['repository_snapshot_id', 'model_version_id', 'prediction_horizon_days'])
