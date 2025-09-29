from typing import Union
from pydantic import BaseModel, Field, constr

# ----- ML -----
class PredictRequest(BaseModel):
    age: float = Field(..., ge=0, lt=120)
    subject_instrument: str = Field(..., min_length=1)
    city: str = Field(..., min_length=1)
    month: Union[str, int] = Field(..., description="e.g. 'January' or 1")

class PredictResponse(BaseModel):
    predicted_price: float

class TrainResponse(BaseModel):
    mse: float
    r2: float

# ----- Users & Tokens -----
class SignupRequest(BaseModel):
    username: str
    password: constr(min_length=1, max_length=72)  # bcrypt limit

class RemoveUserRequest(BaseModel):
    username: str
    password: constr(min_length=1, max_length=72)

class AddTokensRequest(BaseModel):
    username: str
    credit_card: str
    amount: int = Field(ge=1)

class TokensResponse(BaseModel):
    tokens: int
