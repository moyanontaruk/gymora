// Link is the router's replacement for the <a> tag
import { Link, useNavigate, useLocation } from 'react-router-dom'


//hook exported from AuthContext.jsx
import { useAuth} from '../context/AuthContext.jsx'

import PillNav from './PillNav/PillNav.jsx'

//importing the css file.
import './NavBar.css'

const navItems = [
  { label: 'Home', href: '/' },
  { label: 'Exercises', href: '/exercises' },
  { label: 'Equipment', href: '/equipment' },
  { label: 'Workout History', href: '/workouts' },
  { label: 'Routines', href: '/routines' },
  { label: 'Profile', href: '/profile' },
  { label: 'Assistant', href: '/assistant' },
]

function NavBar() {
  //taking only these 2 out of the object the provider shares
  const{ isLoggedIn, logout} = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  function handleLogout() {
    logout()

    //send to homepage after loggingout
    navigate ('/')
  }

  return (
    // <nav> is HTML tag (same as <div>) it means "this is navigation"
    // useful for screen readers, which matters for NFR5
    <nav className="navbar">

        <PillNav
          logo="/GymoraNavLogo.png"
          logoAlt="Gymora — Repping with reason"
          items={navItems}
          activeHref={location.pathname}
          baseColor="#112250"
          pillColor="#ceac68"
          hoveredPillTextColor="#f5f0e9"
          pillTextColor="#112250"
          initialLoadAnimation={false}
        />

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
