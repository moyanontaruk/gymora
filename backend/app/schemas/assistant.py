from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


#what the client SENDS...just the question
class AssistantAsk(BaseModel):

    #min_length stops an empty question reaching the LLM.
        #max_length stops user from overkill prompts which would waste tokens
            #could also push the real data out of the prompt
    question: str = Field(..., min_length=3, max_length=500)


#what the api sends back after asking
class AssistantAnswer(BaseModel):
    message_id: int
    question: str
    response: str

    #NFR4. true when the assistant said the data doesn't cover it
    insufficient_information_flag: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


#one past message...for the history list
class AssistantMessageRead(BaseModel):
    message_id: int
    question: str
    response: str | None = None
    insufficient_information_flag: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)