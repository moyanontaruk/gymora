import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'

import { apiGet } from '../api/client.js'

import './ExerciseDetail.css'


function ExerciseDetail() {

    //reads the id out of the url. the name must match the route,
        //which will be /exercises/:exerciseId
    const { exerciseId } = useParams()

    const [exercise, setExercise] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)


    useEffect(() => {
        async function loadExercise() {
            try {
                //apiGet not apiGetAuth. browsing is public, same as
                    //the library page
                const data = await apiGet(`/exercises/${exerciseId}`)
                setExercise(data)
            }
            catch (err) {
                setError(err.message)
            }
            finally {
                setLoading(false)
            }
        }

        loadExercise()

    //refetch if the id changes, so going straight from one exercise
        //to another still works
    }, [exerciseId])


    if (loading) {
        return <p className="status">Loading exercise...</p>
    }


    if (error) {
        return (
            <section className="exercise-detail-page">
                <p className="status">Could not load this exercise.</p>

                <Link to="/exercises" className="btn btn-outline">
                    Back to exercises
                </Link>
            </section>
        )
    }


    return (
        <section className="exercise-detail-page">

            <Link to="/exercises" className="back-link">
                Back to exercises
            </Link>

            <h1>{exercise.name}</h1>

            <div className="detail-tags">

                {exercise.muscle_groups.map((mg) => {
                    return (
                        <span className="tag" key={mg.muscle_group_id}>
                            {mg.name}
                        </span>
                    )
                })}

                {exercise.equipment.map((eq) => {
                    return (
                        <span className="tag tag-equipment" key={eq.equipment_id}>
                            {eq.name}
                        </span>
                    )
                })}

                {exercise.difficulty_level && (
                    <span className="tag tag-difficulty">
                        {exercise.difficulty_level}
                    </span>
                )}
            </div>


            <div className="detail-body">

                <div className="detail-main">

                    {exercise.description && (
                        <div className="detail-block">
                            <h2>About this exercise</h2>
                            <p>{exercise.description}</p>
                        </div>
                    )}

                    {exercise.instructions && (
                        <div className="detail-block">
                            <h2>How to do it</h2>
                            <p>{exercise.instructions}</p>
                        </div>
                    )}

                    {/*plenty of wger entries have neither, so say so
                    rather than showing an empty page*/}
                    {!exercise.description && !exercise.instructions && (
                        <div className="detail-block">
                            <p className="no-detail">
                                No description available for this exercise yet.
                            </p>
                        </div>
                    )}
                </div>


                {/*the image sits beside the text on a wide screen,
                below it on a narrow one*/}
                {exercise.media_url && (
                    <div className="detail-image">
                        
                        
                        {/*alt describes the image for screen readers.
                            ...using the exercise name, since that's
                            ///what the picture shows*/}
                        <img
                            src={exercise.media_url}
                            alt={exercise.name}
                        />

                        {/*wger's data is CC-BY-SA
                        so attribution is required wherever it's displayed*/}
                        <span className="image-credit">
                            Image from wger, CC BY-SA 4.0
                        </span>
                    </div>
                )}
            </div>


            <div className="detail-actions">
                <Link to="/workouts/new" className="btn btn-solid">
                    Log a workout with this
                </Link>
            </div>
        </section>
    )
}

export default ExerciseDetail