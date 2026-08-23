#used AI to help import wger

#imports wger exercises, mapping their anatomical muscle names onto
    #Gymora's 10 beginner friendly muscle groups
#safe to run more than once, already imported exercises get skipped

#built in. turns &amp; and friends back into normal characters
import html

#built in. used to strip <p> tags out of descriptions
import re

#for pacing/backing off between LLM calls so I don't blow through
    #groq's free-tier rate limit
import time

import requests
from sqlalchemy import select

from app.database import SessionLocal
from app.models.muscle_group import MuscleGroup
from app.models.equipment import Equipment
from app.models.exercise import Exercise
from app.models.exercise_muscle_group import ExerciseMuscleGroup
from app.models.exercise_equipment import ExerciseEquipment
from app.services.llm import ask_llm, LLMError


WGER_BASE = "https://wger.de/api/v2"
ENGLISH = 2

#deliberately small since wger has like 828 exercises
HOW_MANY = 500


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
#only needed here when I want to rename or merge wger's own name.
    #anything not listed just uses wger's name as-is (see sync_equipment_from_wger)
EQUIPMENT_MAP = {
    2: "Barbell",             # SZ-Bar, a barbell variant
    9: "Bench",               # Incline bench
    7: "Bodyweight",          # none (bodyweight exercise)
    4: "Bodyweight",          # Gym mat, floor work
    6: "Pull-up Bar",         # wger spells it "Pull-up bar"
    11: "Resistance Band",    # wger spells it "Resistance band"
    12: "Cable Machine",      # wger spells it "Cable machine"
}


DIFFICULTY_LEVELS = {"beginner", "intermediate", "advanced"}

#groq's free tier throttles fast - one classification call per exercise
    #will 429 almost immediately without pacing + backoff
LLM_PACING_SECONDS = 3
LLM_MAX_RETRIES = 4
LLM_RETRY_BASE_SECONDS = 15


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


#AI-generated (Claude, via Claude Code). asked it for a way to add new
    #equipment types without manually typing names into seed.py
def sync_equipment_from_wger(db, equipment_lookup):
    #pulls wger's full equipment list (their own dedicated endpoint, not
        #the per-exercise one) and makes sure every type has a row here.
        #returns wger_equipment_id -> MY equipment name, covering every id
        #wger has, not just the ones I bothered to rename in EQUIPMENT_MAP
    response = requests.get(
        WGER_BASE + "/equipment/",
        params={"limit": 100},
        timeout=30,
    )
    response.raise_for_status()
    wger_equipment_list = response.json()["results"]

    wger_id_to_my_name = {}
    created = 0

    for wger_equipment in wger_equipment_list:
        wger_id = wger_equipment["id"]

        #fall back to wger's own name when I haven't asked for a rename/merge
        my_name = EQUIPMENT_MAP.get(wger_id, wger_equipment["name"])
        wger_id_to_my_name[wger_id] = my_name

        if my_name not in equipment_lookup:
            equipment = Equipment(name=my_name)
            db.add(equipment)

            #need the id right away in case another wger id maps to the same name
            db.flush()

            equipment_lookup[my_name] = equipment.equipment_id
            created = created + 1

    print("equipment synced from wger, newly created:", created)
    return wger_id_to_my_name


#AI-generated (Claude, via Claude Code). asked it for a way to assign
    #difficulty automatically since wger has no difficulty data of its own
    #and labeling ~500 exercises by hand wasn't practical
def classify_difficulty(name, description, muscle_names, equipment_names):
    #wger has no difficulty rating of its own, so an LLM guesses one
        #from the name/description/muscles/equipment instead of leaving it blank
    system_prompt = (
        "You classify strength exercises by difficulty for a beginner-friendly "
        "fitness app. Reply with exactly one word: beginner, intermediate, or "
        "advanced. No punctuation, no explanation."
    )

    details = [f"Exercise: {name}"]

    if muscle_names:
        details.append(f"Muscles worked: {', '.join(muscle_names)}")

    if equipment_names:
        details.append(f"Equipment: {', '.join(equipment_names)}")

    if description:
        details.append(f"Description: {description}")

    user_message = "\n".join(details)

    reply = None
    for attempt in range(1, LLM_MAX_RETRIES + 1):
        try:
            reply = ask_llm(system_prompt, user_message)
            break
        except LLMError as exc:
            #429s are the free-tier rate limit - worth waiting out.
                #anything else (network, bad response shape) probably won't
                #fix itself, so don't burn retries on it
            is_rate_limited = "busy" in str(exc).lower()
            if is_rate_limited and attempt < LLM_MAX_RETRIES:
                time.sleep(LLM_RETRY_BASE_SECONDS * attempt)
                continue

            print("difficulty classification failed for", name, "-", exc)
            return None

    #space calls out even on success, so the NEXT call doesn't trip the limit
    time.sleep(LLM_PACING_SECONDS)

    guess = reply.strip().lower()
    if guess in DIFFICULTY_LEVELS:
        return guess

    print("unexpected difficulty reply for", name, "-", repr(reply))
    return None


#AI-generated (Claude, via Claude Code). same request as classify_difficulty
    #above - this is the part that applies it to exercises that already
    #existed before that function existed
def backfill_missing_difficulty(db):
    #catches exercises left over from before this script classified difficulty
        #(e.g. a wger import that ran before this feature existed) -
        #those get skipped by the "already imported" check above, so they'd
        #otherwise stay blank forever
    missing = db.execute(
        select(Exercise).where(Exercise.difficulty_level.is_(None))
    ).scalars().all()

    classified = 0

    for exercise in missing:
        muscle_names = [m.name for m in exercise.muscle_groups]
        equipment_names = [e.name for e in exercise.equipment]

        difficulty_level = classify_difficulty(
            exercise.name,
            exercise.description,
            muscle_names,
            equipment_names,
        )

        if difficulty_level is not None:
            exercise.difficulty_level = difficulty_level
            classified = classified + 1

            #commit as I go - this loop can take a long time (pacing +
                #retries per exercise) so a later interruption shouldn't
                #throw away everything classified so far
            db.commit()

    print("backfilled difficulty for", classified, "of", len(missing), "exercises")


#AI-generated (Claude, via Claude Code). follow-up to sync_equipment_from_wger
    #above - reconciles exercises that were imported before a given equipment
    #type existed locally, so they retroactively pick up the missing link
def backfill_equipment_links(db, exercise, wger_exercise, equipment_lookup, wger_equipment_names):
    #for an exercise that already existed before this run - wger might list
        #equipment for it that has no local row yet at import time (e.g. Swiss
        #Ball used to be skipped entirely). reconcile without duplicating
        #links that are already there
    current_ids = {equipment.equipment_id for equipment in exercise.equipment}
    added = 0

    for wger_equipment_item in wger_exercise.get("equipment") or []:
        my_name = wger_equipment_names.get(wger_equipment_item["id"])
        if my_name not in equipment_lookup:
            continue

        equipment_id = equipment_lookup[my_name]
        if equipment_id in current_ids:
            continue

        db.add(
            ExerciseEquipment(
                exercise_id=exercise.exercise_id,
                equipment_id=equipment_id,
            )
        )
        current_ids.add(equipment_id)
        added = added + 1

    return added


def import_from_wger():
    db = SessionLocal()

    try:
        # 1. load my tables into name -> id lookups 

        muscle_lookup = {}
        for muscle_group in db.execute(select(MuscleGroup)).scalars().all():
            muscle_lookup[muscle_group.name] = muscle_group.muscle_group_id

        equipment_lookup = {}
        for equipment in db.execute(select(Equipment)).scalars().all():
            equipment_lookup[equipment.name] = equipment.equipment_id

        print("my muscle groups:", len(muscle_lookup))
        print("my equipment before sync:", len(equipment_lookup))

        #adds any equipment type wger has that I don't yet
            #instead of relying on someone hand-typing names into seed.py
        wger_equipment_names = sync_equipment_from_wger(db, equipment_lookup)
        db.commit()

        print("my equipment after sync:", len(equipment_lookup))

        #2. fetch 

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
        equipment_links_added = 0

        #3. loop and save 

        for wger_exercise in wger_exercises:

            wger_id = str(wger_exercise["id"])

            translation = pick_english(wger_exercise)
            if translation is None or not translation.get("name"):
                skipped_no_english = skipped_no_english + 1
                continue

            #this is what makes re-running safe, unlike seed.py
            already = db.execute(
                select(Exercise).where(
                    Exercise.source == "wger",
                    Exercise.source_external_id == wger_id,
                )
            ).scalar_one_or_none()

            if already is not None:
                skipped_existing = skipped_existing + 1

                #this exercise was imported before, but wger might now map
                    #to equipment that didn't have a local row back then
                equipment_links_added = equipment_links_added + backfill_equipment_links(
                    db, already, wger_exercise, equipment_lookup, wger_equipment_names
                )
                continue

            #wger's category becomes my exercise_type
            #lowercased b/c my filter is case sensitive and my seed is lowercase
            category = wger_exercise.get("category") or {}
            exercise_type = (category.get("name") or "").lower() or None

            images = wger_exercise.get("images") or []
            media_url = images[0]["image"] if images else None

            description = strip_html(translation.get("description"))

            # >>> figure out muscles + equipment BEFORE creating the exercise,
                #their names feed the difficulty guess below

            #a dict, so each muscle group appears only once
            muscle_rows = {}
            muscle_names = []

            for wger_muscle in wger_exercise.get("muscles") or []:
                my_name = MUSCLE_MAP.get(wger_muscle["id"])
                if my_name in muscle_lookup:
                    muscle_rows[muscle_lookup[my_name]] = True
                    muscle_names.append(my_name)

            for wger_muscle in wger_exercise.get("muscles_secondary") or []:
                my_name = MUSCLE_MAP.get(wger_muscle["id"])
                if my_name in muscle_lookup:

                    #setdefault only writes if the key is absent,
                    #so a secondary can never downgrade a primary
                    muscle_rows.setdefault(muscle_lookup[my_name], False)
                    muscle_names.append(my_name)

            #a set stores each value once, so no duplicate rows
            equipment_ids = set()
            equipment_names = set()

            for wger_equipment_item in wger_exercise.get("equipment") or []:
                my_name = wger_equipment_names.get(wger_equipment_item["id"])
                if my_name in equipment_lookup:
                    equipment_ids.add(equipment_lookup[my_name])
                    equipment_names.add(my_name)

            difficulty_level = classify_difficulty(
                translation["name"],
                description,
                muscle_names,
                sorted(equipment_names),
            )

            exercise = Exercise(
                #[:200] guards against names longer than my String(200) column
                name=translation["name"][:200],
                description=description,
                instructions=None,
                difficulty_level=difficulty_level,
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

            for muscle_group_id, is_primary in muscle_rows.items():
                db.add(
                    ExerciseMuscleGroup(
                        exercise_id=exercise.exercise_id,
                        muscle_group_id=muscle_group_id,
                        is_primary=is_primary,
                    )
                )

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
        print("equipment links backfilled for existing exercises:", equipment_links_added)

        backfill_missing_difficulty(db)

    finally:
        db.close()


if __name__ == "__main__":
    import_from_wger()