"""reset relationships

Revision ID: 598f3761cc6b
Revises: 
Create Date: 2025-02-08 20:24:14.715553

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '598f3761cc6b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('quiz_attempt', schema=None) as batch_op:
        batch_op.add_column(sa.Column('correct_questions', postgresql.ARRAY(sa.String()), nullable=True))
        batch_op.alter_column('started_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
        batch_op.alter_column('score',
               existing_type=sa.INTEGER(),
               type_=sa.Float(),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('quiz_attempt', schema=None) as batch_op:
        batch_op.alter_column('score',
               existing_type=sa.Float(),
               type_=sa.INTEGER(),
               existing_nullable=True)
        batch_op.alter_column('started_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
        batch_op.drop_column('correct_questions')

    # ### end Alembic commands ###
