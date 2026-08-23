import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

//apiGet for the exercise list (public), apiPostAuth to save (needs token)
import { apiGet, apiPostAuth } from '../api/client.js'

import './LogWorkout.css'

function todayAsText() {
  const now = new Date()

  //remove the stuf after T...like the seconds/exact time
  return now.toISOString().split('T')[0]
}



//html input gives back text, even type ="number"
    //empoty box gies ' ' and Number('') is 0 but [0] set isnt a thing
      //empty box should mean "not recorded"...so empty = null
function toNumberOrNull(text){
  if (!text) {
    return null
  }
  return Number(text)
}


function LogWorkout() {

  const[workoutDate, setWorkoutDate] = useState(todayAsText())
  const [title, setTitle] = useState('')
  const[notes, setNotes] = useState('')

  //exercise list from the api, to fill the dropdown
  const[allExercises, setAllExercises] = useState([])

  // holding an array of rows
    //starting with 1 blank row so the form isnt empty
  const [rows, setRows] = useState([
    {exercise_id: '' , sets: '', reps: '', weight: ''},
  ])

  const [error,setError]= useState(null)
  const [submitting, setSubmitting] = useState(false)
  const navigate= useNavigate()

  //load exercise list once to fill dropdown
  useEffect(()=> {
    async function loadExercises() {
      try {
        //limiting to 200 for dropdown
        const data= await apiGet('/exercises/?limit=200')
        setAllExercises(data)
      }
      catch (err) {
        setError('Could not load the exercise list.')
      }
    }
    loadExercises()
  }, [])





  

//~~~~


  //changes ONE field in ONE row.
      //index = which row, field = which box, value = what was typed
  function updateRow(index, field, value) {
    
    //.map builds a new array. react needs a new array to notice change
      //...editing the old one in place keeps the same identity, 
      // so react would see nothing and not redraw
    const updated = rows.map((row, i) => {

      //not the row being edited, hand it back unchanged
      if (i !== index) {
          return row
      }

      //the ... spread operator copies everything from the old row,
          //then [field]: value overwrites just the one that changed.
          //the [ ] around field means "use the VALUE of field as the
          //key name", not the literal word "field"
      return { ...row, [field]: value }
    })

  setRows(updated)
  }


  function addRow() {
    //spread the existing rows into a new array, then add a blank one
    setRows([...rows, { exercise_id: '', sets: '', reps: '', weight: '' }])
  }


  function removeRow(index) {
    //.filter keeps only items where the test returns true,
    //so keep every row whose position is not the one removed
    setRows(rows.filter((row, i) => {
        return i !== index
    }))
  }


  async function handleSubmit(event) {
    event.preventDefault()
    setError(null)

    //only keep rows where an exercise was actually chosen
    const chosen = rows.filter((row) => {
      return row.exercise_id !== ''
    })

    if (chosen.length === 0) {
      setError('Please add at least one exercise.')
      return
    }

    setSubmitting(true)

    try {

      const exerciseList = chosen.map((row, index) => {
        return {
          exercise_id: Number(row.exercise_id),

          sets: toNumberOrNull(row.sets),
          reps: toNumberOrNull(row.reps),
          weight: toNumberOrNull(row.weight),

          //index + 1 so the first exercise is order 1, not 0
          exercise_order: index + 1,
        }
      })

      //build the shape the backend expects, matching WorkoutLogCreate.
        //|| null so an empty box sends null, not an empty string.
          //no user_id here...the backend takes that from the token
      const payload = {
        workout_date: workoutDate,
        title: title || null,
        notes: notes || null,
        exercises: exerciseList,
      }

      await apiPostAuth('/workouts/', payload)

      //send them to the history page to see what they just saved
      navigate('/workouts')
  }
    catch (err) {
      setError(err.message)
  }
    finally {
      setSubmitting(false)
    }
  }


  //CHANGED - was a ternary inside the button.
    //let not const, because the next line might replace it
  let saveButtonText = 'Save Workout'

  if (submitting) {
    saveButtonText = 'Saving...'
  }


  return (
    <section className="log-page">
      <h1>
        Log a Workout
      </h1>

      <form onSubmit={handleSubmit}>

        <div className="form-row">
          <div>
            <label htmlFor="date">
              Date
            </label>
            {/*type="date" gives a real calendar picker, free*/}
            <input
              id="date"
              type="date"
              value={workoutDate}
              onChange={(e) => setWorkoutDate(e.target.value)}
              required
            />
          </div>

          <div>
            <label htmlFor="title">Workout name (optional)</label>
            {/*placeholder = grey hint text shown when the box
            is empty. NOT a value, it vanishes on typing*/}
            <input
              id="title"
              type="text"
              placeholder="e.g. Push day"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>
        </div>

        <h2>
          Exercises
        </h2>

        {/*CHANGED - explicit { } and return inside the map.
        one row of inputs per item in the rows array*/}
        {rows.map((row, index) => {
          return (
            //key uses the index here. normally a bad idea, but
              //these rows have no id until saved, and they're
              //only added or removed, never reordered
            <div className="exercise-row" key={index}>

              {/*<select> is a REAL HTML TAG, a dropdown.
                  same controlled pattern as a text input*/}
              <select
                value={row.exercise_id}
                onChange={(e) => updateRow(index, 'exercise_id', e.target.value)}
              >
                {/*value="" counts as "nothing chosen",
                which is what the filter looks for*/}
                <option value="">
                  Choose an exercise...
                </option>

                {/*CHANGED - explicit return here too*/}
                {allExercises.map((ex) => {
                  return (
                    <option key={ex.exercise_id} value={ex.exercise_id}>
                      {ex.name}
                    </option>
                  )
                })}
              </select>

              {/*min="0" stops negative numbers. still gives
              back TEXT though, which is why
              toNumberOrNull is needed on submit*/}
              <input
                type="number"
                min="0"
                placeholder="Sets"
                value={row.sets}
                onChange={(e) => updateRow(index, 'sets', e.target.value)}
              />

              <input
                type="number"
                min="0"
                placeholder="Reps"
                value={row.reps}
                onChange={(e) => updateRow(index, 'reps', e.target.value)}
              />

              {/*step="0.5" allows half kilos, for plates
              like 2.5kg*/}
              <input
                type="number"
                min="0"
                step="0.5"
                placeholder="Weight kg"
                value={row.weight}
                onChange={(e) => updateRow(index, 'weight', e.target.value)}
              />

              {/*type="button" is inside a form, a
              button with no type defaults to SUBMIT, so
              this would save the workout instead of
              deleting a row*/}
              <button
                type="button"
                className="row-remove"
                onClick={() => removeRow(index)}
              >
                Remove
              </button>
            </div>
          )
        })}

        <button type="button" className="btn btn-outline" onClick={addRow}>
          + Add Exercise
        </button>

        <label htmlFor="notes">Notes (optional)</label>
        {/*<textarea> =a multi-line text box.
        in plain html the text goes between the tags, but
        react uses value= like every other input*/}
        <textarea
          id="notes"
          rows="3"
          placeholder="How did it go?"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
        />

        {error && <div className="auth-error">{error}</div>}

        <button type="submit" className="btn btn-solid" disabled={submitting}>
          {saveButtonText}
        </button>
      </form>
    </section>
  )
}

export default LogWorkout











