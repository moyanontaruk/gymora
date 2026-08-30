// after deploying, this line will change
  //nrylify it's set to render url via an envir. variable
  //import.meta.env is how vite exposes env vars to browser
    //and the name has to start with VITE_ or vite wont include it
const API_URL = import.meta.env.VITE_API_URL ||'http://localhost:8000'
const TOKEN_KEY = 'gymora_token'



//apiGET = Reads and no token
//async == marks a function that has to WAIT
      //for something slow (the network).
export async function apiGet(path) {

  //fetch() == makes an http request.
    //await tells code to pause until the reply arrives
        // w/o it, would get an unfinished request instead of a response
  const response = await fetch(API_URL + path)

  // response.ok is TRUE for status 200-299, FALSE for 400s and 500s.
  // fetch does NOT throw an error on a 404 or 500 - it treats them as
        //a successful reply that happens to carry a bad status.
            //check is needed or failures pass silently
  if (!response.ok) {

    //need ``  for ${} substitution. this is a javascript's version of an f-string
  throw new Error(`Request failed: ${response.status}`)
  }

  // .json() reads the body and turns it into javascript objects.
  // it's also slow, so it needs its own await
  return response.json()
}


export function saveToken(token) {
  //.setItem takes keyName and keyValue
  localStorage.setItem(TOKEN_KEY, token)
}

export function getToken() {
  //.getItem returns stored text or null if nothing is stored under that name
  //return is needed, otherwise this hands back nothing
  return localStorage.getItem(TOKEN_KEY)
}

export function clearToken() {
  //this is what logging out does
  localStorage.removeItem(TOKEN_KEY)
}



//login = sends data but to one specific endpoin, in form format
// URLSearchParams == builds form-encoded data, which is what /auth/token endpoint expects.
  // other endpoints take json, but /auth/token uses OAuth2PasswordRequestForm, 
      // which requires form data instead
export async function login(email, password) {
  const body = new URLSearchParams()

  body.append('username', email)
  body.append('password', password)

  const response = await fetch(API_URL + '/auth/token', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: body,
  })

  if (!response.ok) {
    throw new Error('Incorrect email or password')
  }

  //Token schema will return {access_token, token_type}
  const data = await response.json()
  saveToken(data.access_token)
  return data
}



//this will attach the token so protected endpoints will accept the request
export async function apiGetAuth(path) {
  const token = getToken()

  const response = await fetch(API_URL + path, {
    headers: {
      // this is the Authorization button in /docs.
      //need space after Bearer b/c get_current_user dependency splits on it to find the token
      Authorization: `Bearer ${token}`,
    },
  })

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`)
  }

  return response.json()
}




//register in the API client

//.
//.
//.

//register = sends data but no token, not logged in ye
//calls POST /auth/register
  //unlike login, this endpoint takes json, not form data
    //only /auth/token uses form data b/c of OAuth2PasswordRequestForm
export async function register(username, email,password) {
  const response=await fetch(API_URL + '/auth/register',{
    method:'POST',
    headers: {
      //tells server the body is json
      'Content-Type': 'application/json',
    },

    //JSON.stringify = turns object into jsonn string 
        //b/c http bodies are text, not objects
        //names here match UserCreate scheme: username, email, password
    body: JSON.stringify({
      username: username,
      email: email,
      password: password,
    }),
  })


  if (!response.ok){

    //retrieving the one already written in the regisster endpoint
      //opens the response body
    const data = await response.json()

    //reads the message out of the response body
      //if detail missing, fall back on generic message instead
    throw new Error(data.detail || 'Could not create account')
  }

      //endpoint returns new user, shaped by UserRead
      //no token b/c user will still need to log in after registering
        //page will call login() separely after
  return response.json()
}






//apiGetAuth = reads, sends token
//like apiGetAuth but SENDS data. used for creating workouts
    //body is a javascript object, this turns it into json
    //to create, needs to both send JSON data and prove who you are
      //nothing did both yet so thats why we have this
      //path = where to send ('/workouts/')
      //body = data - jsx obj
export async function apiPostAuth(path, body) {
  const token = getToken()



  ///api_url+path builds localhost
  //method:'post' ...b/c fetch defaults to GET. 
      //so w/o this line, it would hit list endpoint instead of create endpoint
  const response = await fetch(API_URL + path, {
    method: 'POST',
    
    //headers= labels attached to request, info aboout the mesage
      //not the message itself
    headers: {
      //tells server how the body is formatted so FastAPI knows to parse to JSON
      'Content-Type': 'application/json',

      //this is what get_current_reads
      Authorization: `Bearer ${token}`,
    },

    //since HTTP can only read text, this converts jsx object into text version of it
    body: JSON.stringify(body),
  })




  if (!response.ok) {
    // let and not const b/c the lines below might replace the message
      //const would not be able to change   
    let message = `Request failed: ${response.status}`


    //inner try
    //FastAPI end returns JSON error 
        //but if it's nanother type of error (crashed server/proxy time out)
            // it migt retyrb HTML
        //w/o guard, attempts to read a better message would itself crash
    //so like... try to improven the message but if fails, keep fall back
    
    try {
      const data = await response.json()

      if (data.detail && !Array.isArray(data.detail)) {
        message = data.detail
      }
      else if (Array.isArray(data.detail)) {
        message = 'Some fields were invalid. Please check the form.'
      }
    }
    catch {
      //body wasn't json. keep the generic message
    }

    throw new Error(message)
  }

  return response.json()
}



//the assisant part
  //the 2 below wrap apiGetAuth and apiPostAuth w/ right path
    //so page don't have  url str randomly through it

    //if endpoint ever moves, it'll just change here only


//loads old questions/answers so chat isn't empty 
export async function getAssistantMessages() {
  return apiGetAuth('/assistant/messages')
}

export async function  askAssistant(question) {
  
  //key name "question" b/c it must match the AssisantAsk Schema on backend
  return apiPostAuth('/assistant/ask',{question})
}







//routines
    //generate returns a routine w/o saving it, so the user can
    //look at it first. save is a separate call

//sends the preferences form, gets back a routine to preview
export async function generateRoutine(preferences) {
  return apiPostAuth('/routines/generate', preferences)
}


//saves a routine the user decided to keep.
    //this is the one that actually writes to the database
export async function saveRoutine(routine) {
  return apiPostAuth('/routines/', routine)
}


//the list for the routines page. summary only, no exercises
export async function getRoutines() {
  return apiGetAuth('/routines/')
}


//one routine with all its exercises nested
export async function getRoutine(routineId) {
  //backticks for the ${} substitution
  return apiGetAuth(`/routines/${routineId}`)
}









//DELETE needs its own helper since apiGetAuth and apiPostAuth
    //only do GET and POST
export async function apiDeleteAuth(path) {
  const token = getToken()

  const response = await fetch(API_URL + path, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`)
  }

  //a 204 response has NO body at all, so calling .json() on it
    //would throw. nothing to return here
  return null
}


export async function deleteRoutine(routineId) {
  return apiDeleteAuth(`/routines/${routineId}`)
}






//the profile summary. counts and breakdowns, all for the logged in user
export async function getProfileStats() {
  return apiGetAuth('/stats/profile')
}



//deletes one workout log. reuses apiDeleteAuth, which already handles
    //the token and the empty 204 response
export async function deleteWorkout(workoutId) {
  return apiDeleteAuth(`/workouts/${workoutId}`)
}