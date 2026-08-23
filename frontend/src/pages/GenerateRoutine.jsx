import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { generateRoutine, saveRoutine } from '../api/client.js'

import './GenerateRoutine.css'


//the options for each question. arrays so the buttons are built by
    //looping, instead of writing the same markup four times
const GOALS = ['muscle gain', 'strength', 'fat loss', 'general fitness']
const LEVELS = ['beginner', 'intermediate', 'advanced']
const DAYS = [2, 3, 4, 5, 6]
const LENGTHS = [30, 45, 60, 90]

//the equipment names must match my equipment table exactly
const EQUIPMENT = [
    'Barbell',
    'Dumbbell',
    'Kettlebell',
    'Cable Machine',
    'Resistance Band',
    'Bench',
    'Pull-up Bar',
    'Bodyweight',
]


function GenerateRoutine() {

    //the answers to the form
    const [goal, setGoal] = useState('muscle gain')
    const [level, setLevel] = useState('beginner')
    const [days, setDays] = useState(3)
    const [length, setLength] = useState(60)

    //an array, b/c someone can have several pieces of equipment
    const [equipment, setEquipment] = useState([])

    //the routine that comes back. null until they generate one.
        //this is option B, it lives in state and is NOT in the
        //database until they press save
    const [routine, setRoutine] = useState(null)

    //the name they can edit before saving
    const [routineName, setRoutineName] = useState('')

    const [generating, setGenerating] = useState(false)
    const [saving, setSaving] = useState(false)
    const [error, setError] = useState(null)

    const navigate = useNavigate()


    //adds or removes one piece of equipment from the list
    function toggleEquipment(name) {

        //.includes checks whether something is already in an array
        if (equipment.includes(name)) {

            //take it out. filter keeps everything that ISN'T this one
            const updated = equipment.filter((item) => {
                return item !== name
            })

            setEquipment(updated)
        }
        else {
            //put it in. spread the existing ones then add this
            setEquipment([...equipment, name])
        }
    }


    async function handleGenerate() {
        setError(null)
        setGenerating(true)

        try {
            const preferences = {
                goal: goal,
                experience_level: level,
                days_per_week: days,
                session_length_minutes: length,
                equipment: equipment,
            }

            const result = await generateRoutine(preferences)

            setRoutine(result)

            //prefill the name box with the one the backend suggested
            setRoutineName(result.name)
        }
        catch (err) {
            setError(err.message)
        }
        finally {
            setGenerating(false)
        }
    }


    async function handleSave() {
        setError(null)
        setSaving(true)

        try {
            //building what RoutineCreate expects. note it sends the
                //exercises back, since the backend didn't keep them
            const toSave = {
                name: routineName,
                goal: routine.goal,
                experience_level: routine.experience_level,
                days_per_week: routine.days_per_week,
                session_length_minutes: routine.session_length_minutes,
                target_muscle_group_id: routine.target_muscle_group_id,

                exercises: routine.exercises.map((ex) => {
                    return {
                        exercise_id: ex.exercise_id,
                        day_number: ex.day_number,
                        exercise_order: ex.exercise_order,
                        suggested_sets: ex.suggested_sets,
                        suggested_reps: ex.suggested_reps,
                        rest_seconds: ex.rest_seconds,
                        notes: ex.notes,
                    }
                }),
            }

            await saveRoutine(toSave)

            navigate('/routines')
        }
        catch (err) {
            setError(err.message)
        }
        finally {
            setSaving(false)
        }
    }


    //groups the flat exercise list into days, so the preview can show
        //Day 1, Day 2 and so on. the backend sends one flat array
        //with a day_number on each item
    function exercisesForDay(dayNumber) {
        return routine.exercises.filter((ex) => {
            return ex.day_number === dayNumber
        })
    }


    //builds [1, 2, 3] from days_per_week so I can loop over the days.
        //javascript has no range() like python, so Array.from with a
        //length is the usual way. the _ means "I don't need this
        //argument", it's a convention not syntax
    function dayNumbers() {
        return Array.from({ length: routine.days_per_week }, (_, i) => {
            return i + 1
        })
    }


    let generateButtonText = 'Generate My Routine'

    if (generating) {
        generateButtonText = 'Building your routine...'
    }

    let saveButtonText = 'Save Routine'

    if (saving) {
        saveButtonText = 'Saving...'
    }


    return (
        <section className="generate-page">

            <h1>Generate a Routine</h1>

            <p className="generate-intro">
                Answer a few questions and Gymora will build a plan from
                the exercise library.
            </p>

            <div className="questions">

                <div className="question">
                    <h3>What is your goal?</h3>

                    <div className="options">
                        {GOALS.map((option) => {

                            //working out the class here rather than inline,
                                //so the markup stays readable. the selected
                                //class is what makes a chosen button look chosen
                            let className = 'option'

                            if (goal === option) {
                                className = 'option option-selected'
                            }

                            return (
                                <button
                                    type="button"
                                    key={option}
                                    className={className}
                                    onClick={() => setGoal(option)}
                                >
                                    {option}
                                </button>
                            )
                        })}
                    </div>
                </div>

                <div className="question">
                    <h3>What is your experience level?</h3>

                    <div className="options">
                        {LEVELS.map((option) => {
                            let className = 'option'

                            if (level === option) {
                                className = 'option option-selected'
                            }

                            return (
                                <button
                                    type="button"
                                    key={option}
                                    className={className}
                                    onClick={() => setLevel(option)}
                                >
                                    {option}
                                </button>
                            )
                        })}
                    </div>
                </div>

                <div className="question">
                    <h3>How many days per week?</h3>

                    <div className="options">
                        {DAYS.map((option) => {
                            let className = 'option'

                            if (days === option) {
                                className = 'option option-selected'
                            }

                            return (
                                <button
                                    type="button"
                                    key={option}
                                    className={className}
                                    onClick={() => setDays(option)}
                                >
                                    {option}
                                </button>
                            )
                        })}
                    </div>
                </div>

                <div className="question">
                    <h3>How long is each session?</h3>

                    <div className="options">
                        {LENGTHS.map((option) => {
                            let className = 'option'

                            if (length === option) {
                                className = 'option option-selected'
                            }

                            return (
                                <button
                                    type="button"
                                    key={option}
                                    className={className}
                                    onClick={() => setLength(option)}
                                >
                                    {option} min
                                </button>
                            )
                        })}
                    </div>
                </div>

                <div className="question">
                    <h3>What equipment can you use?</h3>

                    <p className="question-hint">
                        Leave all unselected to use the whole library.
                    </p>

                    <div className="options">
                        {EQUIPMENT.map((option) => {
                            let className = 'option'

                            if (equipment.includes(option)) {
                                className = 'option option-selected'
                            }

                            return (
                                <button
                                    type="button"
                                    key={option}
                                    className={className}
                                    onClick={() => toggleEquipment(option)}
                                >
                                    {option}
                                </button>
                            )
                        })}
                    </div>
                </div>
            </div>

            {error && <div className="auth-error">{error}</div>}

            <button
                type="button"
                className="btn btn-solid generate-btn"
                onClick={handleGenerate}
                disabled={generating}
            >
                {generateButtonText}
            </button>

            {/*the preview. only appears once a routine exists*/}
            {routine && (
                <div className="preview">

                    <h2>Your Routine</h2>

                    {/*the LLM's explanation. only shows if it came back,
                        since the routine still works without it*/}
                    {routine.explanation && (
                        <div className="explanation">
                            <h3>Why this routine</h3>
                            <p>{routine.explanation}</p>
                        </div>
                    )}

                    <label htmlFor="routine-name">Routine name</label>
                    <input
                        id="routine-name"
                        type="text"
                        value={routineName}
                        onChange={(e) => setRoutineName(e.target.value)}
                    />

                    {dayNumbers().map((dayNumber) => {
                        return (
                            <div className="day-card" key={dayNumber}>

                                <h3>Day {dayNumber}</h3>

                                <ul className="day-exercises">
                                    {exercisesForDay(dayNumber).map((ex) => {
                                        return (
                                            <li key={ex.exercise_id}>
                                                <span className="exercise-name">
                                                    {ex.exercise?.name || `Exercise #${ex.exercise_id}`}
                                                </span>

                                                <span className="detail">
                                                    {ex.suggested_sets} x {ex.suggested_reps}
                                                </span>
                                            </li>
                                        )
                                    })}
                                </ul>
                            </div>
                        )
                    })}

                    <button
                        type="button"
                        className="btn btn-solid save-btn"
                        onClick={handleSave}
                        disabled={saving}
                    >
                        {saveButtonText}
                    </button>
                </div>
            )}
        </section>
    )
}

export default GenerateRoutine