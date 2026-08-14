//Context is React's answer.. put a value in 1 place and any component can read it directly
  //even if it's nested
import { createContext, useContext, useState } from 'react'

//"login as apiLogin" --- renaming an import.
  //it's here b/c i want to call my own function login() below but 2 things can't share a name in same folder
import { getToken, saveToken, clearToken, login as apiLogin } from '../api/client.js'


//creates the container.
//null = the default value if a component reads it from outside the provider
const AuthContext = createContext(null)


// { children } ---prop holding whatever sits INSIDE this component when it's used. 
//// so if I write <AuthProvider><App /></AuthProvider>, then children is <App />
export function AuthProvider({ children }) {

  //useState(getToken()) == "start with whatever is already in localStorage". 
      //this keeps you logged in after a page refresh
  const [token, setToken] = useState(getToken())

  //wraps the client.js login and also updates state
  async function login(email, password) {
    const data = await apiLogin(email, password)

    // client.js already saved it to localStorage.
    // this line puts it in REACT STATE, which is what makes the nav bar redraw
    setToken(data.access_token)

    return data
  }


  async function logout() {
    clearToken()
    setToken(null)
  }


  // !! --converts anything to a true/false. 
     //a token string becomes true, null becomes false.
      //expose it as a plain boolean rather than making every component check the token itself
  const isLoggedIn = !!token

  //{{}} double curly braces means javascript value here
      //inner pair = javascript object (kinda like python dict)
      // so passing 1 objecct containing 4 things
  return (
    <AuthContext.Provider value={{ token, isLoggedIn, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}


//this is a shortcut so components write useAuth() instead of useContext(AuthContext) every time
export function useAuth() {
  return useContext(AuthContext)
}