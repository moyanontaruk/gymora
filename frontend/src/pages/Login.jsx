import { useState } from "react"

// useNavigate --moves the user to another page from inside javascript, 
        // rather than by clicking a link
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from "../context/AuthContext.jsx"
import './Login.css'


function Login() {
    const[email,setEmail] =useState('')
    const[password, setPassword] =useState('')
    const[error, setError] =useState(null)
    const[submitting,setSubmitting] =useState(false)

    //pulls login out of the shared auth context,
        //this saves the token and updates react state
            //which makes the nav bar switch to "Log Out" w/o refresh
    const {login} =  useAuth()


    //calling the hook to give function
    const navigate =useNavigate()


    // event = browser passes it  in auto when the form is submitted
    async function handleSubmit(event) {
        
        //submitting a form by default will reload the page 
            //and that wipes everything so this will stop that 
        event.preventDefault()

        setError(null)
        setSubmitting(true)



        try{
            //calls the function from client.js 
                //it saves the tokens iteself
            await login(email,password)

            //sending user back to homepage once loggin in
            navigate ('/')
        }

        catch(err){
            setError(err.message)
        }
        finally{
            setSubmitting(false)
        }
    }

    return (
        <section className = "auth-page">

            <div className = "auth-card">
                <h1>
                    Welcome Back
                </h1>

                <p className = "auth-subtitle">
                Log in to continue your fitness journey.
                </p>

                <form onSubmit={handleSubmit}>
                    <label htmlFor="email">
                        Email address
                    </label>

                    {/*input is selfclosing*/}
                    {/*(e)=> is an arrow function
                        //e.target is input element
                        //.value is what's currently typed in it
                    //onChange refreshes React state every time users types in new keys
                        if only value={emaill}.. users could type but it would just keep showing empty spaces
                1. user types m
                2. onChange fires w/ e.target.value ="m"
                3. setEmail("m") updates state
                4. state changed, so react re-renders
                5. value={email} now reads "m" so the box shows m */}
                    <input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                
                    required
                    />

                    <label htmlFor="password">
                        Password
                    </label>

                    {/*need type="passward b/c it hides the characters as dots*/}
                    <input
                        id="password" 
                        type="password"
                        value={password}
                        onChange={(e)=> setPassword(e.target.value)}
                        required 
                    />

                    {/*&& = if error is not nul, show div
                    if error is null, render nothing*/}
                    {error && <div className="auth-error">{error}</div>}


                    {/*type="submit" .... makes button trigger the form's onSubmit
                    isable = stops double clicking while request pending*/}
                    <button type="submit" className="btn btn-solid" disabled={submitting}>
                        {submitting ? 'Logging in...' : 'Log in'}
                    </button>
                </form>

                <p className="auth-footer">
                    Don't have an account?
                        <Link to="/register">
                         Create one
                        </Link>
                </p>
            </div>
        </section>
    )
}

export default Login



