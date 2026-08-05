// a page component. same shape as App - a function returning markup

import { Link } from "react-router-dom"
import './Home.css'


//remember to caps H so react know's it' a component
function Home() {
  return (
    <section className="hero">
      <h1 className="hero-title">
      insert logo xxxx one workout at a time.
          {/* br is a line break and it's self closing so slash is needed*/}
      <br />
      xxxxxRepping with reason... one workout at a time.
      </h1>

      <p className="hero-text">
        xxxxxxxxBuild confidence in the gym, one workout at a time. Explore exercises, equipment and workout designed to help you start strong.
         <br />
        Step by step.
      </p>


      {/*btn fills the button with color vs having it seethru*/}
      <div className= "hero-buttons">
          <Link to="/workouts" className="btn btn-solid">
          Start a workout
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
        <div className="card">
          <h3>Workouts</h3>
          <p>Structured sessions to reach your goals.</p>
        </div>

        <div className="card">
          <h3>Routines</h3>
          <p>Follow or build routines that fit your life.</p>
        </div>

        <div className="card">
          <h3>Exercises</h3>
          <p>Browse exercises with step by step guides.</p>
        </div>

        <div className="card">
          <h3>Equipment</h3>
          <p>Explore exercises by machines and free weights.</p>
        </div>
      </div>
    </section>
  )
}

export default Home