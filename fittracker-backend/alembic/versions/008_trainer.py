"""008_trainer - Trainer features: programs, days, exercises, assignments"""
from alembic import op
import sqlalchemy as sa

revision = '008_trainer'
down_revision = '007_challenges'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('workout_programs',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('trainer_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('duration_weeks', sa.Integer, default=4, server_default='4'),
        sa.Column('difficulty', sa.String(20), default='intermediate', server_default='intermediate'),
        sa.Column('is_public', sa.Boolean, default=False, server_default='0'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )
    op.create_table('program_days',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('program_id', sa.Integer, sa.ForeignKey('workout_programs.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('week_number', sa.Integer, nullable=False),
        sa.Column('day_number', sa.Integer, nullable=False),
        sa.Column('name', sa.String(200)),
    )
    op.create_table('program_exercises',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('day_id', sa.Integer, sa.ForeignKey('program_days.id', ondelete='CASCADE'), nullable=False),
        sa.Column('exercise_id', sa.Integer, sa.ForeignKey('exercise_library.id', ondelete='CASCADE'), nullable=False),
        sa.Column('exercise_order', sa.Integer, default=1, server_default='1'),
        sa.Column('sets', sa.Integer, default=3, server_default='3'),
        sa.Column('reps', sa.String(50)),
        sa.Column('weight_note', sa.String(100)),
        sa.Column('rest_seconds', sa.Integer, default=90, server_default='90'),
    )
    op.create_table('program_assignments',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('program_id', sa.Integer, sa.ForeignKey('workout_programs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('client_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('trainer_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('assigned_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('start_date', sa.TIMESTAMP(timezone=True)),
        sa.Column('status', sa.String(20), default='active', server_default='active'),
    )


def downgrade():
    op.drop_table('program_assignments')
    op.drop_table('program_exercises')
    op.drop_table('program_days')
    op.drop_table('workout_programs')
