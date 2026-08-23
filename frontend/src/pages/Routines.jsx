import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'

import { getRoutines, deleteRoutine } from '../api/client.js'

import './Routines.css'


//outside the component b/c it doesn't need state
function formatDate(isoString) {
    const date = new Date(isoString)

    return date.toLocaleDateString('en-GB', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
    })
}


function Routines() {

    const [routines, setRoutines] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)


    useEffect(() => {
        async function loadRoutines() {
            try {
                const data = await getRoutines()
                setRoutines(data)
            }
            catch (err) {
                setError(err.message)
            }
            finally {
                setLoading(false)
            }
        }

        loadRoutines()
    }, [])


    async function handleDelete(routineId) {

        //window.confirm is built into the browser. shows a yes/no box
            //and returns true or false. deleting without asking is
            //the kind of thing testers complain about
        const sure = window.confirm('Delete this routine? This cannot be undone.')

        if (!sure) {
            return
        }

        try {
            await deleteRoutine(routineId)

            //remove it from state too, so the page updates without
                //needing to refetch the whole list
            const remaining = routines.filter((routine) => {
                return routine.routine_id !== routineId
            })

            setRoutines(remaining)
        }
        catch (err) {
            setError(err.message)
        }
    }


    if (loading) {
        return <p className="status">Loading your routines...</p>
    }


    if (error) {
        return <p className="status">Could not load routines: {error}</p>
    }


    //the empty state gets its own early return, same pattern as
        //the workouts page
    if (routines.length === 0) {
        return (
            <section className="routines-page">

                <h1>Your Routines</h1>

                <Link to="/routines/generate" className="btn btn-solid">
                    Generate a Routine
                </Link>

                <div className="empty-state">
                    <p>You haven't saved any routines yet.</p>
                    <p className="empty-hint">
                        Generate one and it will appear here.
                    </p>
                </div>
            </section>
        )
    }


    return (
        <section className="routines-page">

            <h1>Your Routines</h1>

            <Link to="/routines/generate" className="btn btn-solid">
                Generate a Routine
            </Link>

            <div className="routine-list">

                {routines.map((routine) => {
                    return (
                        <div className="routine-card" key={routine.routine_id}>

                            <div className="routine-main">

                                {/*the whole card isn't a link, b/c there's
                                a delete button inside it. a link
                                inside a link doesn't work*/}
                                <Link
                                    to={`/routines/${routine.routine_id}`}
                                    className="routine-name"
                                >
                                    {routine.name}
                                </Link>

                                <div className="routine-meta">
                                    <span className="tag">{routine.goal}</span>

                                    {routine.experience_level && (
                                        <span className="tag">
                                            {routine.experience_level}
                                        </span>
                                    )}

                                    {routine.days_per_week && (
                                        <span className="tag">
                                            {routine.days_per_week} days/week
                                        </span>
                                    )}
                                </div>

                                <span className="routine-date">
                                    Saved {formatDate(routine.created_at)}
                                </span>
                            </div>

                            <div className="routine-actions">

                                <Link
                                    to={`/routines/${routine.routine_id}`}
                                    className="btn btn-outline routine-view"
                                >
                                    View
                                </Link>

                                <button
                                    type="button"
                                    className="routine-delete"
                                    onClick={() => handleDelete(routine.routine_id)}
                                >
                                    Delete
                                </button>
                            </div>
                        </div>
                    )
                })}
            </div>
        </section>
    )
}

export default Routines