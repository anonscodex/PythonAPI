from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated
import module
from database import SessionLocal, engine
from sqlalchemy.orm import Session


app = FastAPI()
module.Base.metadata.create_all(bind=engine)

class ChoiceBase(BaseModel):
    choice_text: str
    is_correct: bool

class QuestionBase(BaseModel):
    question_text: str
    choices: List[ChoiceBase]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

DbDependency = Annotated[Session, Depends(get_db)]


@app.post("/questions/")
async def create_question(question: QuestionBase, db: DbDependency):
    db_question = module.Question(question_text=question.question_text)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    for choice in question.choices:
        db_choice = module.Choices(choice_text=choice.choice_text, is_correct=choice.is_correct, question_id=db_question.id)
        db.add(db_choice)
    db.commit()
        

@app.get("/questions/{question_id}")
async def read_question(question_id: int, db: DbDependency):
    result = db.query(module.Question).filter(module.Question.id == question_id).first()
    if not result:
        raise HTTPException(status_code =404, detail="Question not found")
    return result

@app.get("/questions")
async def get_all_question( db:DbDependency):
    result = db.query(module.Question).all()
    if not result:
        raise HTTPException(status_code=404, detail="Question not found")
    return result

@app.get("/answer/{question_id}")
async def get_answer(question_id: int, db: DbDependency):
    result = db.query(module.Choices).filter(module.Choices.question_id == question_id, module.Choices.is_correct == True).first()
    if not result:
        raise HTTPException(status_code=404, detail="Answer not found")
    return result
