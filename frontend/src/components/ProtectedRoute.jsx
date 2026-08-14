//This is a component whose whole job is to decide whether to render something. 
// It renders either the page or a redirect but never both.


//move user to url
import { Navigate } from "react-router-dom"


import{useAuth} from '../context/AuthContext.jsx'


//any component thats receiving children gets whatever is nexted inside...
        //<ProtectedRoute>
        //  <Workouts />  <----this is children
        // </ProtectedRoute>
function ProtectedRoute ({children}) {
    const{isLoggedIn} = useAuth()


    //if not loggedd in, render Navigate instead of the page
        //user never sees the protected page
    if (!isLoggedIn) {

        //replace = swaps current history entry instead of adding one, 
            //so browser BACK button doesn't bounce them into the redict again
        return <Navigate to="/login" replace/>
    }

    //logged in so show the page that was wrapped
    return children
}

export default ProtectedRoute