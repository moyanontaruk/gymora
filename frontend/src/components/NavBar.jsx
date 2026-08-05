// Link is the router's replacement for the <a> tag
import { Link } from 'react-router-dom'

//importing the css file.
import './NavBar.css'


function NavBar() {
  return (
    // <nav> is a real HTML tag (same as <div>) it means "this is navigation"
    // useful for screen readers, which matters for NFR5
    <nav className="navbar">

        <Link to="/" className="navbar-logo">GYMORA</Link>

        <div className = "navbar-links">
            <Link to="/">Home</Link>
            <Link to="/exercises">Exercises</Link>
        </div>
    </nav>
  )
}

export default NavBar