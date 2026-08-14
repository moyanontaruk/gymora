import {useState} from 'react'
import {useNavigate, Link } from 'react-router-dom'

//register comes from client.js.
// login comes from the CONTEXT b/c it needs to update react state
import {register } from '../api/client.js'
import { useAuth } from '../context/AuthContext.jsx'

// reusing Login.css, since both pages look the same.
    //dont need for a separate file with identical rules
import './Login.css'


function Register() {
  //one piece of state per input. same pattern as Login,
    //just with username added
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const {login} = useAuth()
  const navigate = useNavigate()

  async function handleSubmit(event) {
    event.preventDefault()
    setError(null)
    setSubmitting(true)

    try {
      //there will be 2 calls in this order
        //1. create account, returns the new user..NOT the token
      await register (username,email,password)

      //2. log them in immediately so they dont have to type it again
        // choose not to sent to /login instead b/c that would be annoyng 
      await login(email,password)

      navigate('/')
    }

    catch (err) {
      //err.message..could be whatever was thrown
        //ex: email already registered
      setError(err.message)
    }
    finally{
      setSubmitting (false)
    }
  }

  return (
    <section className="auth-page">
      <div className="auth-card">
        <h1>
          Create your account
        </h1>
        <p className="auth-subtitle">
          Let's build confidence in the gym.
        </p>

        <form onSubmit={handleSubmit}>
          <label htmlFor="username">
            Username
          </label>
          <input
          id="username"
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required />

          <label htmlFor="email">
            Email address
          </label>
          <input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required />


          <label htmlFor="password">
            Password
          </label>
          {/*minLength =8, only front end validation
          backend doesn't have a length rule.*/}
          <input
          id="password"
          type = "password"
          value ={password}
          onChange= {(e) => setPassword(e.target.value)}
          minLength={8}
          required/>

          <p className="auth-hint">
            Must be at least 8 characters long.
          </p>

          {error && <div className="auth-error"> {error} </div>}

          <button type ="submit" className="btn btn-solid" disabled = {submitting}>
            {submitting ? 'Creating account...' : 'Create Account'}
          </button>
        </form>
        <p className="auth-footer">
          Already have an account? 
            <Link to="/login">
            Log in
            </Link>
        </p>

      </div>
    </section>
  )
}

export default Register