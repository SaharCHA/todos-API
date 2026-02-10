from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI
import models
from database import engine,sessionmaker

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = sessionmaker()
    try:
        yield db
    finally:
        db.close()  

@app.get("/")
async def read_all(db:Annotated[Session, Depends(get_db)]):
    return db.query(models.Todo).all()