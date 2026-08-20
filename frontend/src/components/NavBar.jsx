// Link is the router's replacement for the <a> tag
import {Link, useNavigate } from 'react-router-dom'


//hook exported from AuthContext.jsx
import { useAuth} from '../context/AuthContext.jsx'

//importing the css file.
import './NavBar.css'


function NavBar() {
  //taking only these 2 out of the object the provider shares
  const{ isLoggedIn, logout} = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()

    //send to homepage after loggingout
    navigate ('/')
  }
  
  return (
    // <nav> is HTML tag (same as <div>) it means "this is navigation"
    // useful for screen readers, which matters for NFR5
    <nav className="navbar">

        <Link to="/" className="navbar-logo">
          <img src="/Logo.png" alt="" className="navbar-logo-img" />
  
        </Link>

        <div className = "navbar-links">
            <Link to="/">Home</Link>
            <Link to="/exercises">Exercises</Link>
            <Link to="/workouts">Workout History</Link>
            <Link to ="/assistant"> Assistant </Link>

        </div>

        <div className='navbar-actions'>

          {/* ? condition like python's "a if true condition else b*/}
          {isLoggedIn ? (
            <button onClick={handleLogout} className='nav-btn'>
              Log Out
            </button>
          ) : (
            <Link to= "/login" className='nav-btn'>
              Log In
            </Link>
          )}
        </div>
    </nav>
  )
}

export default NavBar