import { useState, useEffect } from 'react'

import { getAssistantMessages, askAssistant } from '../api/client.js'

import './Assistant.css'


//it's outside the component b/c it doesn't need state.
    //turns the stored timestamp into a readable time
function formatTime(isoString) {
    const date = new Date(isoString)

    //only hrs and mins. the date itself is usually today
    return date.toLocaleTimeString('en-GB', {
        hour: '2-digit',
        minute: '2-digit',
    })
}


function Assistant() {

    //the convo so far. an array, like the workout rows,
        //but this one only ever grows at the end
    const [messages, setMessages] = useState([])

    //what's currently typed in the box
    const [question, setQuestion] = useState('')

    //two separate loading states b/c they mean different things.
        //loadingHistory = fetching past messages when the page opens
        //asking = waiting for an answer to the current question
    const [loadingHistory, setLoadingHistory] = useState(true)
    const [asking, setAsking] = useState(false)

    const [error, setError] = useState(null)


    //load past messages once, when the page appears
    useEffect(() => {
        async function loadHistory() {
            try {
                const data = await getAssistantMessages()
                setMessages(data)
            }
            catch (err) {
                setError('Could not load your previous questions.')
            }
            finally {
                setLoadingHistory(false)
            }
        }

        loadHistory()
    }, [])


    async function handleSubmit(event) {
        event.preventDefault()
        setError(null)

        //.trim() removes spaces from both ends. stops someone
            //sending a message that's only whitespace
        const trimmed = question.trim()

        if (trimmed.length < 3) {
            setError('Please type a longer question.')
            return
        }

        setAsking(true)

        //clear the box straight away, so it feels responsive.
            //saved in trimmed above, so it isn't lost
        setQuestion('')

        try {
            const newMessage = await askAssistant(trimmed)

            //add the new message to the end of the list.
                //...messages spreads the existing ones into a new array
                    //then the new one goes after.
                    //a new array, not the old one edited, so react redraws
            setMessages([...messages, newMessage])
        }
        catch (err) {
            setError(err.message)

            //put the question back in the box 
                //so they don't have to retype it after a failure
            setQuestion(trimmed)
        }
        finally {
            setAsking(false)
        }
    }


    //button text worked out here instead of with a ternary
    let sendButtonText = 'Ask'

    if (asking) {
        sendButtonText = 'Thinking...'
    }


    if (loadingHistory) {
        return <p className="status">
                Loading...
                </p>
    }


    return (
        <section className="assistant-page">

            <h1>
                Gymora Assistant
            </h1>
            <p className="assistant-intro">
                Ask about your own training.
            </p>

            <div className="chat">

                {/*&& so this only shows when there are no messages yet*/}
                {messages.length === 0 && (
                    <div className="chat-empty">
                        <p>
                            Try asking:
                        </p>
                        <ul>
                            <li>What did I train most recently?</li>
                            <li>Which muscle group should I train next?</li>
                            <li>Am I getting stronger on bench press?</li>
                        </ul>
                    </div>
                )}

                {/*each saved message holds BOTH the question and the
                    answer, so one database row becomes two bubbles*/}
                {messages.map((msg) => {
                    return (
                        <div className="exchange" key={msg.message_id}>

                            <div className="bubble bubble-user">
                                <p>
                                    {msg.question}
                                </p>
                                <span className="bubble-time">
                                    {formatTime(msg.created_at)}
                                </span>
                            </div>

                            <div className="bubble bubble-assistant">
                                <p>
                                    {msg.response}
                                </p>

                                {/*NFR4 made visible. when the assistant
                                couldn't answer from the data....
                                say so rather than hiding it*/}
                                {msg.insufficient_information_flag && (
                                    <span className="bubble-flag">
                                        Not enough logged data to answer fully
                                    </span>
                                )}
                            </div>
                        </div>
                    )
                })}

                {/*a placeholder bubble while waiting, so the user can
                see something is happening*/}
                {asking && (
                    <div className="bubble bubble-assistant bubble-waiting">
                        <p>
                            Thinking...
                        </p>
                    </div>
                )}
            </div>

            {error && <div className="auth-error">{error}</div>}

            <form onSubmit={handleSubmit} className="chat-form">

                <label htmlFor="question" className="sr-only">
                    Your question
                </label>

                <input
                    id="question"
                    type="text"
                    placeholder="Ask about your training..."
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    disabled={asking}
                />

                <button type="submit" className="btn btn-solid" disabled={asking}>
                    {sendButtonText}
                </button>
            </form>
        </section>
    )
}

export default Assistant