"""add active default true

Revision ID: c429ff92dde6
Revises: 8db92194ea9a
Create Date: 2025-12-06 07:56:21.398332
"""
from alembic import op
import sqlalchemy as sa


revision = 'c429ff92dde6'
down_revision = '8db92194ea9a'
branch_labels = None
depends_on = None


def upgrade():
    # 1) adiciona a coluna com default temporário (SQLite exige isso)
    with op.batch_alter_table('courses') as batch_op:
        batch_op.add_column(
            sa.Column(
                'active',
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("1")
            )
        )

    # 2) garante que todas as linhas existentes têm valor
    op.execute("UPDATE courses SET active = 1")

    # 3) remove o default da coluna (opcional)
    with op.batch_alter_table('courses') as batch_op:
        batch_op.alter_column('active', server_default=None)


def downgrade():
    with op.batch_alter_table('courses') as batch_op:
        batch_op.drop_column('active')
