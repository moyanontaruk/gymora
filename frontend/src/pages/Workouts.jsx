import { useState, useEffect} from 'react'

//apiGetAuth, not apiGet, b/c this endpoint needs the token
import { apiGetAuth, deleteWorkout } from '../api/client.js'

import './Workouts.css'
import {Link} from 'react-router-dom'



//a small helper thats out the component b/c it doesn't need state
    //turns "2026-08-09" into "9 August 2026"
function formatDate(isoDate) {
    //new Date()= turns a date string into a date object javascript can work with
    const date = new Date(isoDate)
    
    //toLocaleDateString = 'en-GB' gives day-month-year order
        //the object picks which parts to show
    return date.toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}


function Workouts() {
    const [workouts, setWorkouts] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        async function loadWorkouts() {
            try {

                //hits GET /workouts/ with the Bearer token attached
                    //the endpoint filters to the logged-in user automatically
                const data = await apiGetAuth ('/workouts/')
                setWorkouts (data)
            }

            catch (err) {
                setError(err.message)
            }
            finally {
                setLoading (false)
            }
        }
        loadWorkouts()
    }, [])



    //early returns.. each handles a case and sops
        //return ecist the function right away and nothing below runs
            //like the backend so it'll check the exception, get out, 
                //leave the noirmal path at bottom
    if (loading) {
        return <p className="status">
                Loading your workout...
                </p>
    }

    if (error) {
        return <p className="status">
            Could not load workouts: {error}
        </p>
    }


    if (workouts.length === 0) {
        return (
        <section className= "workouts-page">
            <h1>
                Workout History
            </h1>

            <Link to="/workouts/new" className="btn btn-solid">
                Log a Workout
            </Link>

            <div className="empty-state">
                <p> 
                    You haven't logged any workouts yet.
                </p>
                <p className="empty-hint">
                    Once you log a session, it will appear here.
                </p>
            </div>
        </section>
        )
    }

    //if here now, that means loading is good, no error 
        //and at least  workout

    return (
        <section className ="workouts-page">
            <h1>
                Workout History
            </h1>

            <Link to="/workouts/new" className="btn btn-solid">
                Log a workout
            </Link>

            <div className= "workout-list">

                {/*.map will go thru every workout and return 1 card each
                ...closest python equiv. is list compregension*/}
                {workouts.map((workout) => (

                    //key needed to render a list,
                        //react uses it to tell items part
                            //has to be unique so using the db ID
                    <div className="workout-card" key={workout.workout_log_id}>
                        <div className="workout-head">
                            <h3>
                                {workout.title || 'Workout'}
                            </h3>

                            <span className="workout-date">
                                {formatDate(workout.workout_date)}
                            </span>


                            {/*delete calls the handler with this card's id*/}
                            <button
                                className="btn btn-danger"
                                onClick={() => handleDelete(workout.workout_log_id)}
                            >
                                delete
                            </button>

                        </div>

                        {/* adding && so will only show if user has added "notes" */}
                        {workout.notes && (
                            <p className="workout-notes">
                                {workout.notes}
                            </p>
                        )}

                        {/*exercise comes nested inside each worout b/c
                        WorkoutLogRead include them, so it's 1 request, not 2*/}
                        <ul className="exercise-list">
                            {workout.exercises.map((ex) => 
                                <li key={ex.workout_log_exercise_id}>

                                    {/*ex.exercise = nested obj added on backend
                                    ...added ?. b/c if ex.exercise is missing, it gives undefined instead
                                        of crashing.. then  || will fall back to ID*/}
                                    <span className="exercise-name">

                                        {/*substitution needs backticks*/}
                                        {ex.exercise?.name || `Exercise #${ex.exercise_id}`}
                                    </span>

                                    {/*only show sets/reps if both were recorded*/}
                                    {ex.sets && ex.reps && (
                                        <span className="detail">
                                            - {ex.sets} x {ex.reps}
                                        </span>
                                    )}

                                    {ex.weight && (
                                        <span className="detail">
                                            @ {ex.weight}kg
                                        </span>
                                    )}
                                </li>
                            )}
                        </ul>
                    </div>
                ))}
            </div>
        </section>
    )










        //delete one workout, then drop it from the list so the page updates
    async function handleDelete(workoutId) {
        //ask first so a mis-click doesn't wipe a log
        const sure = window.confirm('Delete this workout? This cannot be undone.')
        if (!sure) return

        try {
            await deleteWorkout(workoutId)
            //keep every workout EXCEPT the one just deleted
            setWorkouts((current) =>
                current.filter((w) => w.workout_log_id !== workoutId)
            )
        }
        catch (err) {
            setError(err.message)
        }
    }













}

export default Workouts