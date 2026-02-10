from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, HTTPException, Path,status
import models
from database import engine,sessionmaker

app = FastAPI() # создание приложения FastAPI

models.Base.metadata.create_all(bind=engine) # создание всех таблиц в базе данных, определенных в моделях

def get_db(): # функция для получения сессии базы данных , тоесть для взаимодействия с базой данных
    db = sessionmaker()
    try:
        yield db
    finally:
        db.close()  


db_dependency = Annotated[Session, Depends(get_db)] # создание зависимости для получения сессии базы данных, которая будет использоваться в обработчиках маршрутов для взаимодействия с базой данных

class TodoRequest(BaseModel):
     title: str = Field(min_length=3)
     description: str = Field(min_length=3, max_length=100)
     priority: int = Field(gt=0,lt=6)
     completed: bool

@app.get("/")
async def read_all(db: db_dependency):
    """Получение всех задач из базы данных.""" # обработчик для корневого URL, который возвращает все задачи из базы данных. 
                #Он использует зависимость get_db для получения сессии базы данных и выполняет запрос для получения всех записей из таблицы Todos.
    return db.query(models.Todo).all()


@app.get("/todo/{todo_id}",status_code=200) # обработчик для URL /todo/{todo_id}, который возвращает конкретную задачу по ее идентификатору.
async def read_todo(db: db_dependency, todo_id: int = Path(gt=0)):
        """Получение конкретной задачи по ее идентификатору."""
        todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
        if todo is not None:
            return todo
        raise HTTPException(status_code=404, detail="Todo not found")


@app.post("/todo", status_code=status.HTTP_201_CREATED) # обработчик для URL /todo, который создает новую задачу в базе данных. Он принимает данные задачи в формате JSON, проверяет их с помощью модели TodoRequest и сохраняет новую задачу в базе данных.
async def create_todo(db: db_dependency, todo_request: TodoRequest):
    """добавление новой задачи в базу данных."""
    todo_request = models.Todo(**todo_request.model_dump())
    db.add(todo_request)
    db.commit()
    