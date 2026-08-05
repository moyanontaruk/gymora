// after deploying, this line will changes
const API_URL = 'http://localhost:8000'

//async == marks a function that has to WAIT
      //for something slow (the network).
export async function apiGet(path) {

  {/*localStorge is browser feature that stores text on user's machine
    ... it'll survive page refresh so users don't have to sign on again each time (unlike React State)
    */}
  const TOKEN_KEY = 'gymora_token'

  export function saveToken(token) {
    localStorage
  }

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

