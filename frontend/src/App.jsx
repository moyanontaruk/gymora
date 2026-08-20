// importing named things from a package
// the curly braces mean "pick these specific items out of the package"
import { BrowserRouter, Routes, Route } from 'react-router-dom'

// importing my own file. the ./ means "in a folder next to this one"
import Home from './pages/Home.jsx'
import NavBar from './components/NavBar.jsx'
import Exercises from './pages/Exercises.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import Workouts from './pages/Workouts.jsx'
import ProtectedRoute from './components/ProtectedRoute.jsx'
import LogWorkout from './pages/LogWorkout.jsx'
import Assistant from './pages/Assistant.jsx'

function App() {
  return (
    // BrowserRouter switches on URL handling for everything inside it
    <BrowserRouter>

      {/* OUTSIDE Routes, so it shows on every page */}
      <NavBar />

      {/* Routes = the list of possibilities. only ONE will match and render */}
      <Routes>

      {/* path = the URL. element = what to show for it */}
      <Route path="/" element={<Home />} />

      <Route path="/exercises" element={<Exercises />} />

      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route path="/workouts" element={
        <ProtectedRoute>
          <Workouts />
        </ProtectedRoute>}/>

      <Route path="/workouts/new" element={
        <ProtectedRoute>
          <LogWorkout />
        </ProtectedRoute>}/>

      <Route path ="/assistant" element={
        <ProtectedRoute>
          <Assistant />
        </ProtectedRoute>}/>


      </Routes>
    </BrowserRouter>
  )
}

export default App