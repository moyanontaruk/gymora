from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.assistant_message import AssistantMessage
from app.schemas.assistant import AssistantAsk, AssistantAnswer, AssistantMessageRead
from app.core.dependencies import get_current_user
from app.services.llm import ask_llm, LLMError
from app.services.workout_context import build_context


router = APIRouter(prefix="/assistant", tags=["assistant"])


#the phrase the model is told to use when the data can't answer.
    #kept as a constant so the prompt and the check below can never drift apart...
        #changing it in one place changes both
INSUFFICIENT_PHRASE = "INSUFFICIENT_DATA"


#these are the rules, 
    #they stay active the whole reply. 
        # where NFR4 is  enforced
SYSTEM_PROMPT = f"""You are Gymora's fitness assistant. You help people
who are new to the gym understand their own training.

RULES:
1. Answer ONLY using the workout data provided in the user's message.
2. Never invent workouts, dates, weights or exercises that are not in the data.
3. If the data does not contain what is needed to answer, reply with
   exactly this word on its own line: {INSUFFICIENT_PHRASE}
   followed by a short, friendly explanation of what is missing.
4. When you state a fact about their training, include the specific date
   and exercise names from the data. For example "you last trained legs
   on 2 August with squats and lunges". Do not refer to the data itself
   with phrases like "according to your data" or "this comes from your
   recent workouts".
5. Never give medical advice, injury diagnosis, or nutrition plans, even
   if the workout data seems relevant. For any question about pain,
   injury or illness, say clearly that you cannot help with that and
   suggest speaking to a qualified professional such as a doctor or
   physiotherapist. Do not frame this as missing information.
6. Keep answers short and encouraging. Avoid gym jargon, and explain any
   technical term you do use.
7. You may mention general training principles, but any claim about THIS
   person must come from the data.
8. Write dates in a natural format like "9 August", not "2026-08-09"."""



@router.post("/ask", response_model=AssistantAnswer, status_code=status.HTTP_201_CREATED)
def ask_assistant(
    payload: AssistantAsk,
    db: Session = Depends(get_db),

    #the whole point of RAG..
        #the assistant can only see the data belonging to whoever the token says they are.
    current_user: User = Depends(get_current_user),
):

    #STEP 1 ~~retrieval =pull this user's own rows and format them
    context = build_context(db, current_user.user_id)

    #STEP 2 ~~ build the message
        #context 1st then question after
            #so the model reads the data before it reads the request
    user_message = f"""WORKOUT DATA:
{context}

QUESTION:
{payload.question}"""

    #STEP 3 ~ ask the model
    try:
        answer = ask_llm(SYSTEM_PROMPT, user_message)
    except LLMError as exc:
        #503 = service unavailable. the right code for "a thing I
            #depend on is down", rather than 500 which would imply
            #my own code broke
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )

    #STEP 4- did the model say it couldnt answer?
        #checking for the exact phrase it was told to use
    flagged = INSUFFICIENT_PHRASE in answer

    #strip the marker out so the user doesn't see it.
        #.replace swaps every occurrence
        #.strip removes
        #leading and trailing whitespace left behind
    if flagged:
        answer = answer.replace(INSUFFICIENT_PHRASE, "").strip()

    #STEP 5 - save the record. question, answer, AND the context it was based on
        #so any answer can be audited later
    message = AssistantMessage(
        user_id=current_user.user_id,
        question=payload.question,
        response=answer,
        context_used=context,
        insufficient_information_flag=flagged,
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


#past conversations so the chat doesn't start empty every visit
@router.get("/messages", response_model=list[AssistantMessageRead])
def list_messages(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    statement = (
        select(AssistantMessage)

        #NFR2 again. only this user's messages
        .where(AssistantMessage.user_id == current_user.user_id)

        #oldest first, so the chat reads top to bottom
        .order_by(AssistantMessage.created_at)
    )

    return db.execute(statement).scalars().all()