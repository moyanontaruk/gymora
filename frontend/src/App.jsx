//  <App />        {/* my component, the function I wrote */}
//  <app />        {/* a HTML tag called "app" — doesn't exist, silently renders nothing */}




// function App(){
//   return (
//     <div>
//       <h1>Gymora</h1>
//       <p>Frontend is running.</p>
//       </div>
//   )
// }

// export default App






// importing named things from a package
// the curly braces mean "pick these specific items out of the package"
import { BrowserRouter, Routes, Route } from 'react-router-dom'

// importing my own file. the ./ means "in a folder next to this one"
import Home from './pages/Home.jsx'

import NavBar from './components/NavBar.jsx'
import Exercises from './pages/Exercises.jsx'

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

    
      </Routes>
    </BrowserRouter>
  )
}

export default App