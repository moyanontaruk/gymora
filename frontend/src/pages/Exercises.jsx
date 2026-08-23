// useState - like an empty template so changing it causes a re-render 
// useEffect - render immediately with empty state, fetch, then re-render when data loads

import {Link} from 'react-router-dom'
import {useState, useEffect } from 'react'


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

  //--- the dropdown options, fetched once ---
  const [muscleGroups, setMuscleGroups] = useState([])
  const [equipmentList, setEquipmentList] = useState([])


  //--- the filter values. '' means "no filter" ---
  const [search, setSearch] = useState('')
  const [muscleGroup, setMuscleGroup] = useState('')
  const [equipment, setEquipment] = useState('')
  const [difficulty, setDifficulty] = useState('')



    //load the dropdown options ONCE. these don't change,
        //so this useEffect keeps its empty []
  useEffect(() => {
      async function loadOptions() {
          try {
              const groups = await apiGet('/muscle-groups/')
              setMuscleGroups(groups)

              const equipment = await apiGet('/equipment/')
              setEquipmentList(equipment)
          }
          catch (err) {
              //not fatal. the exercise list still works without
                  //the dropdowns being populated
              console.error('Could not load filter options')
          }
      }

      loadOptions()
  }, [])


  //load the exercises. THIS one re-runs whenever a filter changes
  useEffect(() => {

    async function loadExercises() {
      setLoading(true)

      try {
        //URLSearchParams builds the ?a=1&b=2 part of a url
          //and handles escaping, so a search for "pull-up"
          //or a name with a space doesn't break the url
        const params = new URLSearchParams()

        params.append('limit', '500')

        //only add a filter if the user actually chose one.
          //sending muscle_group='' would match nothing
        if (search) {
          params.append('search', search)
        }

        if (muscleGroup) {
          params.append('muscle_group', muscleGroup)
        }

        if (equipment) {
          params.append('equipment', equipment)
        }

        if (difficulty) {
          params.append('difficulty_level', difficulty)
        }

        //.toString() turns it into "limit=100&search=press"
        const data = await apiGet('/exercises/?' + params.toString())

        setExercises(data)
        setError(null)
      }
      catch (err) {
          setError(err.message)
      }
      finally {
          setLoading(false)
        }
    }

    loadExercises()

  //this array is NOT empty.
      //react re-runs the effect whenever ANY of these values change.
      //so picking a muscle group refetches with that filter applied.
      //leaving the array out entirely would loop forever, because
      //the fetch causes a redraw which would trigger the effect again
  }, [search, muscleGroup, equipment, difficulty])


  //clears everything at once
  function clearFilters() {
    setSearch('')
    setMuscleGroup('')
    setEquipment('')
    setDifficulty('')
  }


  return (
    <section className="exercise-page">

      <h1>Exercise Library</h1>

      <div className="filters">

        <div className="filter-field">
          <label htmlFor="search">Search</label>
          <input
            id="search"
            type="text"
            placeholder="e.g. press"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <div className="filter-field">
          <label htmlFor="muscle">Muscle group</label>
          <select
            id="muscle"
            value={muscleGroup}
            onChange={(e) => setMuscleGroup(e.target.value)}
          >
          {/*value="" is the "no filter" option*/}
          <option value="">All muscle groups</option>

          {muscleGroups.map((mg) => {
            return (
              <option key={mg.muscle_group_id} value={mg.name}>
                {mg.name}
              </option>
              )
            })}
          </select>
        </div>

        <div className="filter-field">
          <label htmlFor="equipment">Equipment</label>
          <select
            id="equipment"
            value={equipment}
            onChange={(e) => setEquipment(e.target.value)}
          >
            <option value="">All equipment</option>

            {equipmentList.map((eq) => {
                return (
                  <option key={eq.equipment_id} value={eq.name}>
                    {eq.name}
                  </option>
                )
              })}
          </select>
        </div>

        <div className="filter-field">
            <label htmlFor="difficulty">Difficulty</label>
            {/*these three are typed by hand because difficulty
            is a plain text column with no lookup table.
            the values must match what's stored, lowercase*/}
            <select
              id="difficulty"
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value)}
            >
              <option value="">Any difficulty</option>
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
        </div>

        <button type="button" className="btn btn-outline" onClick={clearFilters}>
          Clear
        </button>
      </div>


    {error && <div className="auth-error">{error}</div>}

    {loading && <p className="status">Loading exercises...</p>}

    {/*&& with a comparison. only show the count when
    loading has finished*/}
    {!loading && (
      <p className="count">{exercises.length} exercises found</p>
    )}

    {/*the "nothing matched" state. easy to hit once someone
    combines two filters, so it needs a real message*/}
    {!loading && exercises.length === 0 && (
      <div className="empty-state">
        <p>No exercises match those filters.</p>
      </div>
    )}










      <div className="exercise-grid">
        {exercises.map((ex) => {
          return (
            //a Link not a div now, so the whole card opens the
              //detail page. backticks for the ${} substitution
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
    </section>
  )
}

export default Exercises