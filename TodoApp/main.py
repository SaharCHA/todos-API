from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, HTTPException, Path
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
    