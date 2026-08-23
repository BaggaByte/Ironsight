"""multi_tenancy

Revision ID: fd3aeaa0424c
Revises: 31845cf10533
Create Date: 2026-08-23 13:03:51.937473

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fd3aeaa0424c'
down_revision: Union[str, Sequence[str], None] = '31845cf10533'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('targets', sa.Column('organization_id', sa.Integer(), server_default='1', nullable=False))
    op.create_foreign_key('fk_targets_org', 'targets', 'organizations', ['organization_id'], ['id'])
    
    op.add_column('scans', sa.Column('organization_id', sa.Integer(), server_default='1', nullable=False))
    op.create_foreign_key('fk_scans_org', 'scans', 'organizations', ['organization_id'], ['id'])
    
    op.add_column('findings', sa.Column('organization_id', sa.Integer(), server_default='1', nullable=False))
    op.create_foreign_key('fk_findings_org', 'findings', 'organizations', ['organization_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_findings_org', 'findings', type_='foreignkey')
    op.drop_column('findings', 'organization_id')
    op.drop_constraint('fk_scans_org', 'scans', type_='foreignkey')
    op.drop_column('scans', 'organization_id')
    op.drop_constraint('fk_targets_org', 'targets', type_='foreignkey')
    op.drop_column('targets', 'organization_id')
