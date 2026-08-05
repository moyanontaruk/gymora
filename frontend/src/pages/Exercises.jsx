// useState - like an empty template so changing it causes a re-render 
// useEffect - render immediately with empty state, fetch, then re-render when data loads
import { useState, useEffect } from 'react'


// ../ means GO UP ONE FOLDER. this file is in pages/, client.js is in
//   api/, then go up to src/ then into api/
import { apiGet } from '../api/client.js'
import './Exercises.css'


function Exercises() {

  // useState = it gives a component MEMORY.
  //it returns 2 things, so unpack them with [ ] :
  //   1. the current value
  //   2. a function to change it
  //the value in useState(...) is the STARTING value.
  //   [] here = start with an empty list, before any data arrives
  const [exercises, setExercises] = useState([])

  //track whether the request is still running, so it show "Loading..." 
      //instead of an empty page. starts true
  const [loading, setLoading] = useState(true)

  //omewhere to put an error message if the request fails.
  //null = nothing wrong yet
  const [error, setError] = useState(null)


  // useEffect =runs code AFTER the component appears on screen. 
      //his is where you fetch data.
  // it takes 2 arguments: a function, and a list
  useEffect(() => {

    //async because it has to wait for the network
    async function loadExercises() {

      try {
        // await =pause here until the api replies
        //limit=xx so the first version stays small
        const data = await apiGet('/exercises/?limit=20')

        // hand the result to react and this redraws the page
        setExercises(data)
      }
      catch (err) {
        setError(err.message)
      }
      // finally = runs whether it worked or failed...like python's finally
      finally {
        setLoading(false)
      }
    }

    // defining the function above doesn't RUN it. this line runs it
    loadExercises()

  // the [ ] at the end is the "dependency list". 
      //EMPTY means "run this once, when the component first appears". 
          //leave it out entirely and it runs after EVERY redraw, 
              // which here would be an infinite loop of api calls
  }, [])





  

  // an early return. if still loading, show this and stop here.
  //   nothing below runs
  if (loading) {
    return <p className="status">Loading exercises...</p>
  }

  if (error) {
    // { } inside jsx = "this is a javascript value, not text".
    //   without braces it would literally print the word "error"
    return <p className="status">Could not load exercises: {error}</p>
  }


  return (
    <section className="exercise-page">
      <h1>Exercise Library</h1>

      {/* {exercises.length} inserts the number of items in the list.
          .length is a REQUIRED property of javascript arrays */}
      <p className="count">{exercises.length} exercises found</p>

      <div className="exercise-grid">

        {/* .map() is a REQUIRED javascript array method. it goes through
            every item and returns a new list - here, one card per exercise.
            this is how react renders a list. closest python equivalent is
            a list comprehension: [make_card(ex) for ex in exercises]

            (ex) => ( ... ) is an "arrow function", javascript shorthand
            for a function. ex is MY CHOICE of name for each item */}
        {exercises.map((ex) => (

          // key is a REQUIRED react prop when rendering a list. react uses
          //   it to tell items apart. it must be UNIQUE - the database id
          //   is perfect. leave it out and react warns in the console
          <div className="exercise-card" key={ex.exercise_id}>

            {/* {ex.name} reads the name field off this exercise.
                these field names come straight from your ExerciseRead
                schema - name, description, muscle_groups, difficulty_level */}
            <h3>{ex.name}</h3>

            <div className="tags">
              {/* a list INSIDE a list. each exercise has several muscle
                  groups, so map over those too */}
              {ex.muscle_groups.map((mg) => (
                <span className="tag" key={mg.muscle_group_id}>
                  {mg.name}
                </span>
              ))}
            </div>

            {/* && is REQUIRED javascript, meaning AND. used here as a
                shortcut: "if difficulty_level exists, show the span".
                if it's null, nothing renders. needed because your wger
                imports have no difficulty set */}
            {ex.difficulty_level && (
              <span className="tag tag-difficulty">{ex.difficulty_level}</span>
            )}
          </div>
        ))}
      </div>
    </section>
  )
}

export default Exercises