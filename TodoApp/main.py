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

@app.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT) # обработчик для URL /todo/{todo_id}, который обновляет существующую задачу по ее идентификатору. Он принимает данные задачи в формате JSON, проверяет их с помощью модели TodoRequest и обновляет соответствующую запись в базе данных.
async def update_todo(db:db_dependency,
                      todo_request: TodoRequest,
                      todo_id: int):
    """Обновление существующей задачи по ее идентификатору."""
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first() # Выборка из базы данных . Сначала вытаскиваем таблицу ,потом сравнивайм id с переданным id и выбираем первую запись которая подходит под условие. Если такой записи нет , то будет возвращено None
    if todo is not None:    # Присваеваем и делаем коммит 
        todo.title = todo_request.title
        todo.description = todo_request.description
        todo.priority = todo_request.priority
        todo.completed = todo_request.completed
        db.commit()
    else: # Id не найден
         raise HTTPException(status_code=404, detail="Todo not found")  

@app.delete("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, todo_id: int = Path(gt=0)):
     todo_request = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
     if todo_request is not None:
        db.delete(todo_request)
        db.commit()
        return
     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Todo not found")