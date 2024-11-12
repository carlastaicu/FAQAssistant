from pydantic import BaseModel, Field
from typing import Optional
from typing import List, Literal

class QuestionRequest(BaseModel):
  user_question: str
  
class AnswerResponse(BaseModel):
    source: str
    matched_question: str
    answer: str
    
class RouteQuery(BaseModel):
    """Route a user query to the most relevant datasource."""
    datasources: List[Literal["it_related", "compliance_agent"]] = Field(
        ...,
        description="Given a user question, choose which datasource would be most relevant for answering the question.",
    )
    
class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
