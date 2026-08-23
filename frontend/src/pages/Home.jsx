// a page component. same shape as App - a function returning markup

import { Link } from "react-router-dom"
import './Home.css'


//remember to caps H so react know's it' a component
function Home() {
  return (
    <section className="hero">

      <img
        src="/GymoraTransparent.png"
        alt="Gymora — Repping with reason. Track. Train. Transform."
        className="hero-logo"
      />

      <p className="hero-text">
        Discover exercises, build routines, track your workouts,
        <br />
        and understand your progress—all in one place.
      </p>


      {/*btn fills the button with color vs having it seethru*/}
      <div className= "hero-buttons">
          <Link to="/workouts" className="btn btn-solid">
          Start a Workout
          </Link>

          <Link to="/exercises" className="btn btn-outline">
          Browse Exercises
          </Link>
      </div>



      {/* "cards" wrapper holding the four feature boxes */}
      <div className="cards">

        {/* h3 not h2, b/c these sit below
            the h1 in importance. heading levels should describe
            structure, not size */}
        <Link to="/workouts"className="card">
          <div className="card-head">
            <img src="/WorkoutHistory.png" alt="" className="card-icon" />
            <h3>Workout History</h3>
          </div>
          <p>Review your past workouts and monitor your progress.</p>
          <span className="card-link">View &rarr;</span>
        </Link>

        <Link to="/routines" className="card">
          <div className="card-head">
            <img src="/Routine.png" alt="" className="card-icon" />
            <h3>Routines</h3>
          </div>
          <p>Follow or build routines that fit your goals.</p>
          <span className="card-link">View &rarr;</span>
        </Link>

        <Link to="/exercises" className="card">
          <div className="card-head">
            <img src="/Dumbbell.png" alt="" className="card-icon" />
            <h3>Exercises</h3>
          </div>
          <p>Browse exercises with step-by-step guides.</p>
          <span className="card-link">View &rarr;</span>
        </Link>

        <Link to="/equipment" className="card">
          <div className="card-head">
            <img src="/plate.png" alt="" className="card-icon" />
            <h3>Equipment</h3>
          </div>
          <p>Explore exercises by machines and free weights.</p>
          <span className="card-link">View &rarr;</span>
        </Link>
      </div>
    </section>
  )
}

export default Home
