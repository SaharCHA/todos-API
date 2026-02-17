
from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, HTTPException, Path,status
from database import db_dependency
import models
from .auth import get_current_user


router = APIRouter() # создание приложения FastAPI

user_dependency = Annotated[dict,Depends(get_current_user)]


class TodoRequest(BaseModel):
     title: str = Field(min_length=3)
     description: str = Field(min_length=3, max_length=100)
     priority: int = Field(gt=0,lt=6)
     completed: bool

@router.get("/")
async def read_all(user:user_dependency, db: db_dependency):
    """Получение всех задач из базы данных.""" 
    if user is None:
        raise HTTPException(status_code=401,detail='Authentication failed')
    return db.query(models.Todos).filter(models.Todos.owner_id == user.get('id')).all()


@router.get("/todo/{todo_id}",status_code=200) # обработчик для URL /todo/{todo_id}, который возвращает конкретную задачу по ее идентификатору.
async def read_todo(user:user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
        """Получение конкретной задачи по ее идентификатору."""
        if user is None:
             raise HTTPException(status_code=401,detail='Authentication failed')
        todo = db.query(models.Todos)\
        .filter(models.Todos.id == todo_id).filter(models.Todos.owner_id == user.get('id')).first()
        if todo is not None:
            return todo
        raise HTTPException(status_code=404, detail="Todo not found")


@router.post("/todo", status_code=status.HTTP_201_CREATED) # обработчик для URL /todo, который создает новую задачу в базе данных. Он принимает данные задачи в формате JSON, проверяет их с помощью модели TodoRequest и сохраняет новую задачу в базе данных.
async def create_todo(user:user_dependency,
                      db: db_dependency, todo_request: TodoRequest):
    """добавление новой задачи в базу данных."""
    if user is None: 
         raise HTTPException(status_code=401,detail='Authentication failed')
    todo_request = models.Todos(**todo_request.model_dump(),owner_id = user.get('id'))
    db.add(todo_request)
    db.commit()

@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT) # обработчик для URL /todo/{todo_id}, который обновляет существующую задачу по ее идентификатору. Он принимает данные задачи в формате JSON, проверяет их с помощью модели TodoRequest и обновляет соответствующую запись в базе данных.
async def update_todo(
     user:user_dependency,
     db:db_dependency,
     todo_request: TodoRequest,
     todo_id: int):
    """Обновление существующей задачи по ее идентификатору."""
    todo = db.query(models.Todos).filter(models.Todos.id == todo_id)\
        .filter(models.Todos.owner_id == user.get('id')).first() # Выборка из базы данных . Сначала вытаскиваем таблицу ,потом сравнивайм id с переданным id и выбираем первую запись которая подходит под условие. Если такой записи нет , то будет возвращено None
    if todo is not None:    # Присваеваем и делаем коммит 
        todo.title = todo_request.title
        todo.description = todo_request.description
        todo.priority = todo_request.priority
        todo.completed = todo_request.completed
        db.commit()
    else: # Id не найден
         raise HTTPException(status_code=404, detail="Todo not found")  

@router.delete("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user:user_dependency,db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401,detail="Authentication failed")
    todo_request = db.query(models.Todos).filter(models.Todos.id == todo_id)\
        .filter(models.Todos.owner_id == user.get('id')).first()
    if todo_request is not None:
        db.delete(todo_request)
        db.commit()
        return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Todo not found")

