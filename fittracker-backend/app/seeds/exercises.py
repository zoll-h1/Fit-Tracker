"""Seed 50 exercises into exercise_library.
Run: python -m app.seeds.exercises
"""
import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal

EXERCISES = [
    # CHEST
    {"name": "Barbell Bench Press", "slug": "barbell-bench-press", "muscle_primary": "chest", "muscle_secondary": "triceps,shoulders", "equipment": "barbell,bench", "force_type": "push", "difficulty": "intermediate", "category": "strength", "met_value": 6.0},
    {"name": "Dumbbell Bench Press", "slug": "dumbbell-bench-press", "muscle_primary": "chest", "muscle_secondary": "triceps,shoulders", "equipment": "dumbbell,bench", "force_type": "push", "difficulty": "beginner", "category": "strength", "met_value": 5.5},
    {"name": "Incline Barbell Bench Press", "slug": "incline-barbell-bench-press", "muscle_primary": "chest", "muscle_secondary": "triceps,shoulders", "equipment": "barbell,bench", "force_type": "push", "difficulty": "intermediate", "category": "strength", "met_value": 6.0},
    {"name": "Cable Fly", "slug": "cable-fly", "muscle_primary": "chest", "muscle_secondary": "shoulders", "equipment": "cable", "force_type": "push", "difficulty": "beginner", "category": "strength", "met_value": 4.5},
    {"name": "Push-Up", "slug": "push-up", "muscle_primary": "chest", "muscle_secondary": "triceps,shoulders", "equipment": "bodyweight", "force_type": "push", "difficulty": "beginner", "category": "strength", "met_value": 3.8},
    # BACK
    {"name": "Barbell Deadlift", "slug": "barbell-deadlift", "muscle_primary": "back", "muscle_secondary": "glutes,hamstrings,traps", "equipment": "barbell", "force_type": "pull", "difficulty": "advanced", "category": "strength", "met_value": 7.0},
    {"name": "Pull-Up", "slug": "pull-up", "muscle_primary": "back", "muscle_secondary": "biceps,shoulders", "equipment": "bodyweight", "force_type": "pull", "difficulty": "intermediate", "category": "strength", "met_value": 5.0},
    {"name": "Barbell Row", "slug": "barbell-row", "muscle_primary": "back", "muscle_secondary": "biceps,rear_delts", "equipment": "barbell", "force_type": "pull", "difficulty": "intermediate", "category": "strength", "met_value": 5.5},
    {"name": "Lat Pulldown", "slug": "lat-pulldown", "muscle_primary": "back", "muscle_secondary": "biceps", "equipment": "cable", "force_type": "pull", "difficulty": "beginner", "category": "strength", "met_value": 5.0},
    {"name": "Seated Cable Row", "slug": "seated-cable-row", "muscle_primary": "back", "muscle_secondary": "biceps,rear_delts", "equipment": "cable", "force_type": "pull", "difficulty": "beginner", "category": "strength", "met_value": 4.5},
    {"name": "Dumbbell Row", "slug": "dumbbell-row", "muscle_primary": "back", "muscle_secondary": "biceps", "equipment": "dumbbell,bench", "force_type": "pull", "difficulty": "beginner", "category": "strength", "met_value": 4.5},
    # SHOULDERS
    {"name": "Overhead Barbell Press", "slug": "overhead-barbell-press", "muscle_primary": "shoulders", "muscle_secondary": "triceps,traps", "equipment": "barbell", "force_type": "push", "difficulty": "intermediate", "category": "strength", "met_value": 5.5},
    {"name": "Dumbbell Lateral Raise", "slug": "dumbbell-lateral-raise", "muscle_primary": "shoulders", "muscle_secondary": "", "equipment": "dumbbell", "force_type": "push", "difficulty": "beginner", "category": "strength", "met_value": 4.0},
    {"name": "Face Pull", "slug": "face-pull", "muscle_primary": "shoulders", "muscle_secondary": "rear_delts,traps", "equipment": "cable", "force_type": "pull", "difficulty": "beginner", "category": "strength", "met_value": 4.0},
    # LEGS
    {"name": "Barbell Squat", "slug": "barbell-squat", "muscle_primary": "quads", "muscle_secondary": "glutes,hamstrings,core", "equipment": "barbell", "force_type": "push", "difficulty": "intermediate", "category": "strength", "met_value": 6.0},
    {"name": "Romanian Deadlift", "slug": "romanian-deadlift", "muscle_primary": "hamstrings", "muscle_secondary": "glutes,back", "equipment": "barbell", "force_type": "pull", "difficulty": "intermediate", "category": "strength", "met_value": 6.0},
    {"name": "Leg Press", "slug": "leg-press", "muscle_primary": "quads", "muscle_secondary": "glutes,hamstrings", "equipment": "machine", "force_type": "push", "difficulty": "beginner", "category": "strength", "met_value": 5.0},
    {"name": "Walking Lunge", "slug": "walking-lunge", "muscle_primary": "quads", "muscle_secondary": "glutes,hamstrings", "equipment": "bodyweight", "force_type": "push", "difficulty": "beginner", "category": "strength", "met_value": 4.5},
    {"name": "Leg Curl", "slug": "leg-curl", "muscle_primary": "hamstrings", "muscle_secondary": "", "equipment": "machine", "force_type": "pull", "difficulty": "beginner", "category": "strength", "met_value": 4.0},
    {"name": "Leg Extension", "slug": "leg-extension", "muscle_primary": "quads", "muscle_secondary": "", "equipment": "machine", "force_type": "push", "difficulty": "beginner", "category": "strength", "met_value": 4.0},
    {"name": "Calf Raise", "slug": "calf-raise", "muscle_primary": "calves", "muscle_secondary": "", "equipment": "machine", "force_type": "push", "difficulty": "beginner", "category": "strength", "met_value": 3.5},
    {"name": "Hip Thrust", "slug": "hip-thrust", "muscle_primary": "glutes", "muscle_secondary": "hamstrings", "equipment": "barbell,bench", "force_type": "push", "difficulty": "intermediate", "category": "strength", "met_value": 5.0},
    # ARMS
    {"name": "Barbell Curl", "slug": "barbell-curl", "muscle_primary": "biceps", "muscle_secondary": "forearms", "equipment": "barbell", "force_type": "pull", "difficulty": "beginner", "category": "strength", "met_value": 4.0},
    {"name": "Dumbbell Curl", "slug": "dumbbell-curl", "muscle_primary": "biceps", "muscle_secondary": "forearms", "equipment": "dumbbell", "force_type": "pull", "difficulty": "beginner", "category": "strength", "met_value": 4.0},
    {"name": "Hammer Curl", "slug": "hammer-curl", "muscle_primary": "biceps", "muscle_secondary": "forearms,brachialis", "equipment": "dumbbell", "force_type": "pull", "difficulty": "beginner", "category": "strength", "met_value": 4.0},
    {"name": "Tricep Pushdown", "slug": "tricep-pushdown", "muscle_primary": "triceps", "muscle_secondary": "", "equipment": "cable", "force_type": "push", "difficulty": "beginner", "category": "strength", "met_value": 4.0},
    {"name": "Skull Crusher", "slug": "skull-crusher", "muscle_primary": "triceps", "muscle_secondary": "", "equipment": "barbell,bench", "force_type": "push", "difficulty": "intermediate", "category": "strength", "met_value": 4.5},
    {"name": "Dips", "slug": "dips", "muscle_primary": "triceps", "muscle_secondary": "chest,shoulders", "equipment": "bodyweight", "force_type": "push", "difficulty": "intermediate", "category": "strength", "met_value": 5.0},
    # CORE
    {"name": "Plank", "slug": "plank", "muscle_primary": "core", "muscle_secondary": "shoulders", "equipment": "bodyweight", "force_type": "static", "difficulty": "beginner", "category": "strength", "met_value": 3.5},
    {"name": "Crunch", "slug": "crunch", "muscle_primary": "core", "muscle_secondary": "", "equipment": "bodyweight", "force_type": "pull", "difficulty": "beginner", "category": "strength", "met_value": 3.0},
    {"name": "Hanging Leg Raise", "slug": "hanging-leg-raise", "muscle_primary": "core", "muscle_secondary": "hip_flexors", "equipment": "bodyweight", "force_type": "pull", "difficulty": "intermediate", "category": "strength", "met_value": 4.0},
    {"name": "Russian Twist", "slug": "russian-twist", "muscle_primary": "core", "muscle_secondary": "obliques", "equipment": "bodyweight", "force_type": "static", "difficulty": "beginner", "category": "strength", "met_value": 3.5},
    {"name": "Ab Wheel Rollout", "slug": "ab-wheel-rollout", "muscle_primary": "core", "muscle_secondary": "shoulders,lats", "equipment": "ab_wheel", "force_type": "push", "difficulty": "advanced", "category": "strength", "met_value": 4.0},
    # CARDIO
    {"name": "Treadmill Run", "slug": "treadmill-run", "muscle_primary": "cardio", "muscle_secondary": "legs", "equipment": "treadmill", "force_type": "push", "difficulty": "beginner", "category": "cardio", "met_value": 9.0},
    {"name": "Stationary Bike", "slug": "stationary-bike", "muscle_primary": "cardio", "muscle_secondary": "legs", "equipment": "bike", "force_type": "push", "difficulty": "beginner", "category": "cardio", "met_value": 7.0},
    {"name": "Rowing Machine", "slug": "rowing-machine", "muscle_primary": "cardio", "muscle_secondary": "back,arms", "equipment": "rower", "force_type": "pull", "difficulty": "intermediate", "category": "cardio", "met_value": 8.5},
    {"name": "Jump Rope", "slug": "jump-rope", "muscle_primary": "cardio", "muscle_secondary": "calves,shoulders", "equipment": "jump_rope", "force_type": "push", "difficulty": "beginner", "category": "cardio", "met_value": 11.0},
    {"name": "Elliptical", "slug": "elliptical", "muscle_primary": "cardio", "muscle_secondary": "legs,arms", "equipment": "elliptical", "force_type": "push", "difficulty": "beginner", "category": "cardio", "met_value": 5.0},
    # COMPOUND / FULL BODY
    {"name": "Power Clean", "slug": "power-clean", "muscle_primary": "back", "muscle_secondary": "legs,shoulders,core", "equipment": "barbell", "force_type": "pull", "difficulty": "advanced", "category": "olympic", "met_value": 8.0},
    {"name": "Kettlebell Swing", "slug": "kettlebell-swing", "muscle_primary": "glutes", "muscle_secondary": "hamstrings,core,back", "equipment": "kettlebell", "force_type": "push", "difficulty": "intermediate", "category": "strength", "met_value": 8.0},
    {"name": "Burpee", "slug": "burpee", "muscle_primary": "cardio", "muscle_secondary": "chest,legs,core", "equipment": "bodyweight", "force_type": "push", "difficulty": "intermediate", "category": "cardio", "met_value": 8.0},
    {"name": "Box Jump", "slug": "box-jump", "muscle_primary": "quads", "muscle_secondary": "glutes,calves", "equipment": "box", "force_type": "push", "difficulty": "intermediate", "category": "strength", "met_value": 8.0},
    {"name": "Battle Ropes", "slug": "battle-ropes", "muscle_primary": "shoulders", "muscle_secondary": "arms,core", "equipment": "ropes", "force_type": "push", "difficulty": "intermediate", "category": "cardio", "met_value": 10.0},
    {"name": "Sled Push", "slug": "sled-push", "muscle_primary": "quads", "muscle_secondary": "glutes,shoulders", "equipment": "sled", "force_type": "push", "difficulty": "intermediate", "category": "strength", "met_value": 9.0},
    # FLEXIBILITY
    {"name": "Foam Rolling", "slug": "foam-rolling", "muscle_primary": "recovery", "muscle_secondary": "", "equipment": "foam_roller", "force_type": "static", "difficulty": "beginner", "category": "flexibility", "met_value": 2.5},
    {"name": "Cat-Cow Stretch", "slug": "cat-cow-stretch", "muscle_primary": "back", "muscle_secondary": "core", "equipment": "bodyweight", "force_type": "static", "difficulty": "beginner", "category": "flexibility", "met_value": 2.0},
    # TRAPS / POSTERIOR CHAIN
    {"name": "Barbell Shrug", "slug": "barbell-shrug", "muscle_primary": "traps", "muscle_secondary": "neck", "equipment": "barbell", "force_type": "pull", "difficulty": "beginner", "category": "strength", "met_value": 4.0},
    {"name": "Dumbbell Shrug", "slug": "dumbbell-shrug", "muscle_primary": "traps", "muscle_secondary": "neck", "equipment": "dumbbell", "force_type": "pull", "difficulty": "beginner", "category": "strength", "met_value": 4.0},
    {"name": "Good Morning", "slug": "good-morning", "muscle_primary": "hamstrings", "muscle_secondary": "back,glutes", "equipment": "barbell", "force_type": "pull", "difficulty": "intermediate", "category": "strength", "met_value": 5.0},
    {"name": "Sumo Deadlift", "slug": "sumo-deadlift", "muscle_primary": "glutes", "muscle_secondary": "quads,hamstrings,back", "equipment": "barbell", "force_type": "pull", "difficulty": "advanced", "category": "strength", "met_value": 7.0},
]


async def seed() -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(text("SELECT COUNT(*) FROM exercise_library"))
        count = result.scalar()
        if count and count > 0:
            print(f"Already seeded ({count} exercises). Skipping.")
            return

        for ex in EXERCISES:
            await db.execute(
                text("""
                    INSERT INTO exercise_library
                        (name, slug, muscle_primary, muscle_secondary, equipment,
                         force_type, difficulty, category, met_value)
                    VALUES
                        (:name, :slug, :muscle_primary, :muscle_secondary, :equipment,
                         :force_type, :difficulty, :category, :met_value)
                    ON CONFLICT (slug) DO NOTHING
                """),
                ex,
            )
        await db.commit()
        print(f"Seeded {len(EXERCISES)} exercises.")


if __name__ == "__main__":
    asyncio.run(seed())
