from database import *
from data_models import *
from auth_handler import *
from utils import *
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from datetime import datetime, timedelta
from typing import Optional
from typing_extensions import Annotated

app = FastAPI()

question_embeddings = None
questions = None
answers = None

# Load and embed questions on application startup
@app.on_event("startup")
async def startup_event():
    # Load the FAQ database
    global question_embeddings, questions, answers
    df_faq = pd.DataFrame(faq_database)

    questions = df_faq['question'].tolist()
    answers = df_faq['answer'].tolist()

    # Embed all questions in the database once and store the embeddings
    question_embeddings = embeddings_model.embed_documents(questions)

@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:

    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/")
def read_root():
    return {"Hello": "Steelsoft"}

@app.post("/ask-question")
async def ask_question(user: str = Depends(get_current_active_user), request: QuestionRequest = None):
    if not request.user_question:
        raise HTTPException(status_code=400, detail="Question is required in the request body")

    # Check if the string is a valid question - ends with '?' and has at least two words
    if not is_question(request.user_question):
        raise HTTPException(
            status_code=400,
            detail="The provided string is not a valid question. A question should contain at least two words and end with '?'"
        )

    try:
        user_question = request.user_question
        answer_response = route_question(user_question, question_embeddings, questions, answers)
        
        return answer_response

    except ValueError as e:
        # Catch invalid data or embedding errors
        raise HTTPException(status_code=500, detail=f"Value error occurred: {str(e)}")

    except HTTPException as e:
        error_message = f"An error occurred: {str(e)}"
        raise HTTPException(status_code=500, detail=error_message)
