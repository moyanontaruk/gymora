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
import MoltenMetal from './components/MoltenMetal/MoltenMetal.jsx'
import GenerateRoutine from './pages/GenerateRoutine.jsx'
import RoutineDetail from './pages/RoutineDetail.jsx'
import Equipment from './pages/Equipment.jsx'
import Profile from './pages/Profile.jsx'
import Routines from './pages/Routines.jsx'
import ExerciseDetail from './pages/ExerciseDetail.jsx'





function App() {
  return (
    // BrowserRouter switches on URL handling for everything inside it
    <BrowserRouter>

      {/* fixed behind everything else, so it shows through as a page-wide backdrop */}
      <div style={{ position: 'fixed', inset: 0, zIndex: -1 }}>
        <MoltenMetal
          color1="#112250"
          color2="#d89e2a"
          color3="#FFFFFF"
          speed={0.55}
          scale={5.2}
          detail={4}
          glow={1.6}
          coreSize={0.1}
          swirl={1}
          fold={-0.2}
          blackPoint={0.05}
          brightness={1.55}
          colorMode="molten"
          grain={true}
          grainIntensity={0.03}
          mouseInteraction={true}
          mouseStrength={0.3}
          opacity={1.0}
        />
      </div>

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

      <Route path="/routines" element={
        <ProtectedRoute>
          <Routines />
        </ProtectedRoute>}/>

      <Route path="/routines/generate" element={
        <ProtectedRoute>
          <GenerateRoutine />
        </ProtectedRoute>}/>

      <Route path="/routines/:routineId" element={
        <ProtectedRoute>
          <RoutineDetail />
        </ProtectedRoute>}/>

      

      <Route path="/profile" element={
        <ProtectedRoute>
          <Profile />
        </ProtectedRoute>}/>

  <Route path="/equipment" element={<Equipment />} />

      <Route path="/exercises/:exerciseId" element={<ExerciseDetail />} />

      </Routes>
    </BrowserRouter>
  )
}

export default App