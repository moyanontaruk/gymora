#calls the groq api. this file knows nothing about workouts or users,
    #it just sends text and gets text back.
    #keeping it separate means that if i wanna swap provider later, itll be in one file

import requests

from app.config import get_settings


settings = get_settings()

#groq's endpoint. the path is the openai standard, which is why
    #a lot of tools work with groq without changes
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


#raised when the api call fails.
    #custom exception type so the router can catch this specifically
        #instead of catching everything and hiding real bugs
class LLMError(Exception):
    pass


#system_prompt = the instructions (who the assistant is, what rules to follow)
#user_message= the question plus the retrieved workout data
def ask_llm(system_prompt: str, user_message: str) -> str:

    headers = {
        #same Bearer pattern as my own api. the key proves who I am
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": settings.groq_model,

        #messages is a LIST, in order. 
            #"role" says who is speaking:
            #system = instructions, sets the rules and stays active the whole time
            #user = what the person said
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],

        #temperature controls randomness, 0 to 2.
            #low = predictable and factual
            #high = creative and varied.
            #0.3 because this assistant should stick to the data,
                #not invent interesting phrasing
        "temperature": 0.3,

        #cap on the reply length, in tokens (roughly 3/4 of a word each).
            #stops a runaway answer and keeps responses readable
        "max_tokens": 500,
    }

    try:
        response = requests.post(
            GROQ_URL,
            headers=headers,
            json=payload,

            #give up after 30 seconds instead of hanging forever.
                #without this a slow api would freeze my endpoint
            timeout=30,
        )
    except requests.RequestException as exc:
        #network failed entirely...b/c no internet, dns failure, timeout
        raise LLMError("Could not reach the assistant service.") from exc

    #429 = too many requests
        #giving its own message b/c the free tier limits are low enough to actually hit during testing
    if response.status_code == 429:
        raise LLMError("The assistant is busy right now. Please try again shortly.")





    # if not response.ok:
    #     raise LLMError("The assistant service returned an error.")

    #if not response.ok:
        #temp - printing groq's actual error to see what's wrong..
        #print("GROQ SAID:", response.status_code, response.text)

        #raise LLMError("The assistant service returned an error.")



    if not response.ok:
        #log groq's actual error to the server console but don't send it to the user..
            #they don't need the provider's internals and the raw response could contain details worth not exposing.
            #this is what showed me the model name had been retired..
        print("GROQ ERROR:", response.status_code, response.text)

        raise LLMError("The assistant service returned an error.")










    data = response.json()

    #digging into groq's response shape:
        #{"choices": [{"message": {"content": "the answer"}}]}
        #.get() with a default at each step so a surprise shape
            #will give a clean error instead of a KeyError crash
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as exc:
        raise LLMError("The assistant returned an unexpected response.") from exc