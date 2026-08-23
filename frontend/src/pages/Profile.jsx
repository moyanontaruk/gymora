import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'

import { getProfileStats } from '../api/client.js'
import { useAuth } from '../context/AuthContext.jsx'

import './Profile.css'


function formatDate(isoString) {
    const date = new Date(isoString)

    return date.toLocaleDateString('en-GB', {
        month: 'long',
        year: 'numeric',
    })
}


function Profile() {

    const [stats, setStats] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    const { logout } = useAuth()


    useEffect(() => {
        async function loadStats() {
            try {
                const data = await getProfileStats()
                setStats(data)
            }
            catch (err) {
                setError(err.message)
            }
            finally {
                setLoading(false)
            }
        }

        loadStats()
    }, [])


    if (loading) {
        return <p className="status">Loading your profile...</p>
    }


    if (error) {
        return <p className="status">Could not load your profile: {error}</p>
    }


    //works out the widest bar, so the others can be sized relative
        //to it. Math.max with ... spreads the array into separate
        //arguments, b/c Math.max takes numbers not a list
    function highestCount() {
        if (stats.muscle_groups.length === 0) {
            return 1
        }

        const counts = stats.muscle_groups.map((mg) => {
            return mg.times_trained
        })

        return Math.max(...counts)
    }


    //turns a count into a percentage width for the bar
    function barWidth(times) {
        const percent = (times / highestCount()) * 100

        //template literal, b/c css needs "45%" not 45
        return `${percent}%`
    }


    return (
        <section className="profile-page">

            <h1>Profile</h1>

            <div className="profile-header">

                <div>
                    <h2>{stats.username}</h2>
                    <p className="profile-email">{stats.email}</p>
                    <p className="profile-since">
                        Member since {formatDate(stats.member_since)}
                    </p>
                </div>

                <button
                    type="button"
                    className="btn btn-outline"
                    onClick={logout}
                >
                    Log Out
                </button>
            </div>


            {/*the headline numbers*/}
            <div className="stat-grid">

                <div className="stat-card">
                    <span className="stat-number">{stats.total_workouts}</span>
                    <span className="stat-label">Workouts logged</span>
                </div>

                <div className="stat-card">
                    <span className="stat-number">
                        {stats.total_exercises_performed}
                    </span>
                    <span className="stat-label">Exercises performed</span>
                </div>

                <div className="stat-card">
                    <span className="stat-number">
                        {stats.workouts_this_month}
                    </span>
                    <span className="stat-label">This month</span>
                </div>

                <div className="stat-card">
                    <span className="stat-number stat-text">
                        {stats.last_trained || 'None yet'}
                    </span>
                    <span className="stat-label">Last trained</span>
                </div>
            </div>


            {/*nothing logged yet so the breakdowns would be empty*/}
            {stats.total_workouts === 0 && (
                <div className="empty-state">
                    <p>You haven't logged any workouts yet.</p>
                    <p className="empty-hint">
                        <Link to="/workouts/new">Log your first workout</Link> to
                        start seeing your progress here.
                    </p>
                </div>
            )}


            {stats.muscle_groups.length > 0 && (
                <div className="profile-section">

                    <h2>Muscle groups trained</h2>

                    <div className="bars">
                        {stats.muscle_groups.map((mg) => {
                            return (
                                <div className="bar-row" key={mg.name}>

                                    <span className="bar-label">{mg.name}</span>

                                    {/*the track the bar sits in*/}
                                    <div className="bar-track">

                                        {/*style={{ }} is REQUIRED double braces.
                                            outer = "javascript value",
                                            inner = an object of css properties.
                                            used here b/c the width is worked out from data
                                                so it can't live in a css file*/}
                                        <div
                                            className="bar-fill"
                                            style={{ width: barWidth(mg.times_trained) }}
                                        />
                                    </div>

                                    <span className="bar-count">
                                        {mg.times_trained}
                                    </span>
                                </div>
                            )
                        })}
                    </div>
                </div>
            )}


            {stats.top_exercises.length > 0 && (
                <div className="profile-section">

                    <h2>Most performed exercises</h2>

                    <ul className="exercise-stats">
                        {stats.top_exercises.map((ex) => {
                            return (
                                <li key={ex.name}>

                                    <span className="exercise-name">{ex.name}</span>

                                    <span className="detail">
                                        {ex.times_performed} times

                                        {/*only show a best weight if one was ever recorded*/}
                                        {ex.best_weight && (
                                            <span className="best-weight">
                                                best {ex.best_weight}kg
                                            </span>
                                        )}
                                    </span>
                                </li>
                            )
                        })}
                    </ul>
                </div>
            )}
        </section>
    )
}

export default Profile