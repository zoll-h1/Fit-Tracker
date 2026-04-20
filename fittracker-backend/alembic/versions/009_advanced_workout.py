"""009_advanced_workout - Cardio, supersets, custom exercises"""
from alembic import op
import sqlalchemy as sa

revision = '009_advanced_workout'
down_revision = '008_trainer'
branch_labels = None
depends_on = None

def upgrade():
    # Add cardio fields to workout_sessions
    op.add_column('workout_sessions', sa.Column('session_type', sa.String(20), server_default='strength'))
    op.add_column('workout_sessions', sa.Column('distance_km', sa.Numeric(6, 2), nullable=True))
    op.add_column('workout_sessions', sa.Column('avg_pace_min_km', sa.Numeric(5, 2), nullable=True))
    op.add_column('workout_sessions', sa.Column('avg_heart_rate', sa.Integer, nullable=True))
    op.add_column('workout_sessions', sa.Column('max_heart_rate', sa.Integer, nullable=True))

    # Add superset grouping to workout_exercises
    op.add_column('workout_exercises', sa.Column('superset_group', sa.Integer, nullable=True))

    # Add user_id for per-user custom exercises
    op.add_column('exercise_library', sa.Column('created_by_user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True))

def downgrade():
    op.drop_column('workout_sessions', 'session_type')
    op.drop_column('workout_sessions', 'distance_km')
    op.drop_column('workout_sessions', 'avg_pace_min_km')
    op.drop_column('workout_sessions', 'avg_heart_rate')
    op.drop_column('workout_sessions', 'max_heart_rate')
    op.drop_column('workout_exercises', 'superset_group')
    op.drop_column('exercise_library', 'created_by_user_id')
