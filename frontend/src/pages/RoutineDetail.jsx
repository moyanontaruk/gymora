import { useState, useEffect } from 'react'

//useParams is a react-router hook. it reads values OUT of the url.
    //my route is /routines/:routineId, so useParams gives me
    //whatever sits in that spot
import { useParams, Link } from 'react-router-dom'

import { getRoutine } from '../api/client.js'

import './RoutineDetail.css'


function RoutineDetail() {
    //the { } is destructuring again. useParams returns an object
        //with one key per url parameter, so this pulls out routineId.
        //the NAME must match the route exactly: /routines/:routineId
    const { routineId } = useParams()

    const [routine, setRoutine] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)


    useEffect(() => {
        async function loadRoutine() {
            try {
                const data = await getRoutine(routineId)
                setRoutine(data)
            }
            catch (err) {
                setError(err.message)
            }
            finally {
                setLoading(false)
            }
        }

        loadRoutine()

    //NOT empty. if the id in the url changes, refetch.
        //matters if the user goes from one routine straight to
        //another without the page unmounting in between
    }, [routineId])


    if (loading) {
        return <p className="status">Loading routine...</p>
    }


    if (error) {
        //a 404 lands here, which is what the backend returns both
            //when a routine doesn't exist AND when it isn't yours
        return (
            <section className="routine-detail-page">
                <p className="status">Could not load this routine.</p>

                <Link to="/routines" className="btn btn-outline">
                    Back to routines
                </Link>
            </section>
        )
    }


    //groups the flat exercise list by day. the backend sends one
        //array with a day_number on each item
    function exercisesForDay(dayNumber) {
        return routine.exercises.filter((ex) => {
            return ex.day_number === dayNumber
        })
    }


    //builds [1, 2, 3] so I can loop over the days
    function dayNumbers() {
        return Array.from({ length: routine.days_per_week }, (_, i) => {
            return i + 1
        })
    }


    return (
        <section className="routine-detail-page">

            <Link to="/routines" className="back-link">
                Back to routines
            </Link>

            <h1>{routine.name}</h1>

            <div className="routine-meta">
                <span className="tag">{routine.goal}</span>

                {routine.experience_level && (
                    <span className="tag">{routine.experience_level}</span>
                )}

                {routine.days_per_week && (
                    <span className="tag">{routine.days_per_week} days/week</span>
                )}

                {routine.session_length_minutes && (
                    <span className="tag">
                        {routine.session_length_minutes} min sessions
                    </span>
                )}
            </div>

            {dayNumbers().map((dayNumber) => {
                return (
                    <div className="day-card" key={dayNumber}>

                        <h2>Day {dayNumber}</h2>

                        <ul className="day-exercises">
                            {exercisesForDay(dayNumber).map((ex) => {
                                return (
                                    <li key={ex.exercise_id}>

                                        <div className="exercise-info">
                                            <span className="exercise-name">
                                                {ex.exercise?.name || `Exercise #${ex.exercise_id}`}
                                            </span>

                                            {/*the muscle groups this exercise
                                                hits, from the nested object*/}
                                            {ex.exercise?.muscle_groups && (
                                                <span className="exercise-muscles">
                                                    {ex.exercise.muscle_groups.map((mg) => {
                                                        return mg.name
                                                    }).join(', ')}
                                                </span>
                                            )}
                                        </div>

                                        <div className="exercise-numbers">
                                            <span className="detail">
                                                {ex.suggested_sets} x {ex.suggested_reps}
                                            </span>

                                            {ex.rest_seconds && (
                                                <span className="rest">
                                                    {ex.rest_seconds}s rest
                                                </span>
                                            )}
                                        </div>
                                    </li>
                                )
                            })}
                        </ul>
                    </div>
                )
            })}
        </section>
    )
}

export default RoutineDetail