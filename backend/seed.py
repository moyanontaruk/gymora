#small manual seed test before doing the external api with wger

from app.database import SessionLocal
from app.models.muscle_group import MuscleGroup
from app.models.equipment import Equipment
from app.models.exercise import Exercise

MUSCLE_GROUPS = ["Chest", 
                 "Back", 
                 "Shoulders", 
                 "Biceps", 
                 "Triceps", 
                 "Quadriceps", 
                 "Hamstrings", 
                 "Glutes", 
                 "Calves", 
                 "Core"]

EQUIPMENT = ["Barbell",
             "Dumbbell",
             "Kettlebell",
             "Cable Machine",
             "Resistance Band",
             "Bench",
             "Pull-up Bar",
             "Bodyweight"]

EXERCISES = [
    ("Push-up", "beginner", "strength"),
    ("Bodyweight Squat", "beginner", "strength"),
    ("Plank", "beginner", "core"),
    ("Dumbbell Bench Press", "beginner", "strength"),
    ("Lat Pulldown", "beginner", "strength"),
    ("Barbell Deadlift", "intermediate", "strength"),
    ("Barbell Bench Press", "intermediate", "strength"),
    ("Pull-up", "intermediate", "strength"),
    ("Walking Lunge", "intermediate", "strength"),
    ("Barbell Back Squat", "intermediate", "strength"),
    ("Overhead Press", "intermediate", "strength"),
    ("Bent-over Row", "intermediate", "strength"),
]

def seed():

    #unlike before where FastAPI created the session, this isn't a web request/no FastAPI involved
    #opening session myself directly from SessionLocal from factory that was built in database.py
    db=SessionLocal()
    try:
        for name in MUSCLE_GROUPS:
            db.add(MuscleGroup(name=name))

        for name in EQUIPMENT:
            db.add(Equipment(name=name))

        for name, difficulty, ex_type in EXERCISES:
            db.add(Exercise(name=name,
                            difficulty_level = difficulty,
                            exercise_type =ex_type,
                            source="manual_seed", ))
            
        db.commit()
        print("seeding complete")

    finally:
        db.close()

if __name__ == "__main__":
    seed()