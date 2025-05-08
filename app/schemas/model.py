from pydantic import BaseModel, EmailStr


class Predict(BaseModel):
    model_id: int = 1
    match_link: str = "https://www.hltv.org/matches/2381658/favbet-vs-ruby-exort-series-9"