#imports wger exercises, mapping their anatomical muscle names onto
    #Gymora's 10 beginner friendly muscle groups
#safe to run more than once, already imported exercises get skipped

#built in. turns &amp; and friends back into normal characters
import html

#built in. used to strip <p> tags out of descriptions
import re

import requests
from sqlalchemy import select

from app.database import SessionLocal
from app.models.muscle_group import MuscleGroup
from app.models.equipment import Equipment
from app.models.exercise import Exercise
from app.models.exercise_muscle_group import ExerciseMuscleGroup
from app.models.exercise_equipment import ExerciseEquipment


WGER_BASE = "https://wger.de/api/v2"
ENGLISH = 2

#deliberately small since wger has like 828 exercises
HOW_MANY = 60


#wger muscle id -> MY muscle group name
#this dict IS the jargon-to-plain-english translation
MUSCLE_MAP = {
    4: "Chest",        # Pectoralis major
    3: "Chest",        # Serratus anterior
    12: "Back",        # Latissimus dorsi
    9: "Back",         # Trapezius
    2: "Shoulders",    # Anterior deltoid
    1: "Biceps",       # Biceps brachii
    13: "Biceps",      # Brachialis
    5: "Triceps",      # Triceps brachii
    10: "Quadriceps",  # Quadriceps femoris
    11: "Hamstrings",  # Biceps femoris
    8: "Glutes",       # Gluteus maximus
    7: "Calves",       # Gastrocnemius
    15: "Calves",      # Soleus
    6: "Core",         # Rectus abdominis
    14: "Core",        # Obliquus externus abdominis
}


#wger equipment id -> MY equipment name
#None = I have no matching category, skip it
EQUIPMENT_MAP = {
    1: "Barbell",
    2: "Barbell",           
            # SZ-Bar, a barbell variant
    3: "Dumbbell",
    10: "Kettlebell",
    12: "Cable Machine",
    11: "Resistance Band",
    8: "Bench",
    9: "Bench",             
            # Incline bench
    6: "Pull-up Bar",
    7: "Bodyweight",        
            # none (bodyweight exercise)
    4: "Bodyweight",        
            # Gym mat, floor work
    5: None,                
            # Swiss Ball, no equivalent
}


def strip_html(raw_text):
    #descriptions arrive as html like "<p>Lie on a bench</p>"
    if raw_text is None:
        return None

    #find every <...> and swap it for a space
    without_tags = re.sub(r"<[^>]+>", " ", raw_text)
    unescaped = html.unescape(without_tags)

    #.split() with no argument splits on any whitespace and drops blanks
    #re-joining tidies up the gaps the tag removal left behind
    return " ".join(unescaped.split())


def pick_english(exercise_data):
    #wger keeps names and descriptions in a separate list, one entry per language
    for translation in exercise_data.get("translations", []):
        if translation.get("language") == ENGLISH:
            return translation

    return None


def import_from_wger():
    db = SessionLocal()

    try:
        # ---------- 1. load MY tables into name -> id lookups 

        muscle_lookup = {}
        for muscle_group in db.execute(select(MuscleGroup)).scalars().all():
            muscle_lookup[muscle_group.name] = muscle_group.muscle_group_id

        equipment_lookup = {}
        for equipment in db.execute(select(Equipment)).scalars().all():
            equipment_lookup[equipment.name] = equipment.equipment_id

        print("my muscle groups:", len(muscle_lookup))
        print("my equipment:", len(equipment_lookup))

        # ------ 2. fetch 

        response = requests.get(
            WGER_BASE + "/exerciseinfo/",
            params={"limit": HOW_MANY, "language": ENGLISH},
            timeout=60,
        )
        response.raise_for_status()
        wger_exercises = response.json()["results"]

        print("fetched from wger:", len(wger_exercises))

        imported = 0
        skipped_existing = 0
        skipped_no_english = 0

        # ---- 3. loop and save 

        for wger_exercise in wger_exercises:

            wger_id = str(wger_exercise["id"])

            translation = pick_english(wger_exercise)
            if translation is None or not translation.get("name"):
                skipped_no_english = skipped_no_english + 1
                continue

            #THIS is what makes re-running safe, unlike seed.py
            already = db.execute(
                select(Exercise).where(
                    Exercise.source == "wger",
                    Exercise.source_external_id == wger_id,
                )
            ).scalar_one_or_none()

            if already is not None:
                skipped_existing = skipped_existing + 1
                continue

            #wger's category becomes my exercise_type
            #lowercased b/c my filter is case sensitive and my seed is lowercase
            category = wger_exercise.get("category") or {}
            exercise_type = (category.get("name") or "").lower() or None

            images = wger_exercise.get("images") or []
            media_url = images[0]["image"] if images else None

            exercise = Exercise(
                #[:200] guards against names longer than my String(200) column
                name=translation["name"][:200],
                description=strip_html(translation.get("description")),
                instructions=None,

                #wger has no difficulty rating. left empty on purpose
                    #maybe come back to it later if time
                difficulty_level=None,

                exercise_type=exercise_type,
                source="wger",
                source_external_id=wger_id,
                media_url=media_url[:500] if media_url else None,
                is_active=True,
                created_by_user_id=None,
            )

            db.add(exercise)

            #flush sends the INSERT so postgres assigns exercise_id,
            #but does NOT commit. I need that id for the join rows below
                #leaves the transaction open b/c if something fails, 
                    #the single commit means nothing gets saved
            db.flush()



            # >>> muscle join rows

            #a dict, so each muscle group appears only once
            muscle_rows = {}

            for wger_muscle in wger_exercise.get("muscles") or []:
                my_name = MUSCLE_MAP.get(wger_muscle["id"])
                if my_name in muscle_lookup:
                    muscle_rows[muscle_lookup[my_name]] = True

            for wger_muscle in wger_exercise.get("muscles_secondary") or []:
                my_name = MUSCLE_MAP.get(wger_muscle["id"])
                if my_name in muscle_lookup:

                    #setdefault only writes if the key is absent,
                    #so a secondary can never downgrade a primary
                    muscle_rows.setdefault(muscle_lookup[my_name], False)

            for muscle_group_id, is_primary in muscle_rows.items():
                db.add(
                    ExerciseMuscleGroup(
                        exercise_id=exercise.exercise_id,
                        muscle_group_id=muscle_group_id,
                        is_primary=is_primary,
                    )
                )



            # >>> equipment join rows 

            #a set stores each value once, so no duplicate rows
            equipment_ids = set()

            for wger_equipment in wger_exercise.get("equipment") or []:
                my_name = EQUIPMENT_MAP.get(wger_equipment["id"])
                if my_name in equipment_lookup:
                    equipment_ids.add(equipment_lookup[my_name])

            for equipment_id in equipment_ids:
                db.add(
                    ExerciseEquipment(
                        exercise_id=exercise.exercise_id,
                        equipment_id=equipment_id,
                    )
                )

            imported = imported + 1

        db.commit()

        print()
        print("imported:", imported)
        print("skipped, already there:", skipped_existing)
        print("skipped, no english name:", skipped_no_english)

    finally:
        db.close()


if __name__ == "__main__":
    import_from_wger()