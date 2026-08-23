import { useState, useEffect } from 'react'

import { apiGet } from '../api/client.js'

import './Equipment.css'
import { Link} from 'react-router-dom'


function Equipment() {

    const [equipment, setEquipment] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    //which piece of equipment is selected. null = none picked yet
    const [selected, setSelected] = useState(null)

    //the exercises using the selected equipment
    const [exercises, setExercises] = useState([])
    const [loadingExercises, setLoadingExercises] = useState(false)


    //load the equipment list once
    useEffect(() => {
        async function loadEquipment() {
            try {
                const data = await apiGet('/equipment/')
                setEquipment(data)
            }
            catch (err) {
                setError(err.message)
            }
            finally {
                setLoading(false)
            }
        }

        loadEquipment()
    }, [])


    //load exercises whenever the selection changes.
        //not an empty dependency array so this reruns on each pick
    useEffect(() => {

        //nothing selected yet, so nothing to fetch
        if (!selected) {
            return
        }

        async function loadExercises() {
            setLoadingExercises(true)

            try {
                //reusing the exercise filter I already built.
                    //encodeURIComponent escapes spaces and symbols,
                    //so "Cable Machine" and "Pull-up Bar" work
                const name = encodeURIComponent(selected)
                const data = await apiGet(`/exercises/?equipment=${name}&limit=100`)

                setExercises(data)
            }
            catch (err) {
                setError(err.message)
            }
            finally {
                setLoadingExercises(false)
            }
        }

        loadExercises()
    }, [selected])


    if (loading) {
        return <p className="status">Loading equipment...</p>
    }


    if (error) {
        return <p className="status">Could not load equipment: {error}</p>
    }


    return (
        <section className="equipment-page">

            <h1>Equipment</h1>

            <p className="equipment-intro">
                Pick a piece of equipment to see the exercises that use it.
            </p>

            <div className="equipment-grid">

                {equipment.map((item) => {

                    //working out the class above the markup, same
                        //pattern as the routine option buttons
                    let className = 'equipment-card'

                    if (selected === item.name) {
                        className = 'equipment-card equipment-card-selected'
                    }

                    return (
                        <button
                            type="button"
                            key={item.equipment_id}
                            className={className}
                            onClick={() => setSelected(item.name)}
                        >
                            <h3>{item.name}</h3>

                            {item.description && (
                                <p>{item.description}</p>
                            )}
                        </button>
                    )
                })}
            </div>

            {/*only shows once something has been picked*/}
            {selected && (
                <div className="equipment-results">

                    <h2>Exercises using {selected}</h2>

                    {loadingExercises && (
                        <p className="status">Loading exercises...</p>
                    )}

                    {!loadingExercises && exercises.length === 0 && (
                        <div className="empty-state">
                            <p>No exercises found for {selected}.</p>
                        </div>
                    )}

                    <div className="exercise-grid">
                        {exercises.map((ex) => {
                            return (
                                <Link
                                    to={`/exercises/${ex.exercise_id}`}
                                    className="exercise-card"
                                    key={ex.exercise_id}
                                >

                                    <h3>{ex.name}</h3>

                                    <div className="tags">
                                        {ex.muscle_groups.map((mg) => {
                                            return (
                                                <span className="tag" key={mg.muscle_group_id}>
                                                    {mg.name}
                                                </span>
                                            )
                                        })}

                                        {ex.difficulty_level && (
                                            <span className="tag tag-difficulty">
                                                {ex.difficulty_level}
                                            </span>
                                        )}
                                    </div>
                                </Link>
                            )
                        })}
                    </div>
                </div>
            )}
        </section>
    )
}

export default Equipment