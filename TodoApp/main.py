from fastapi import  FastAPI
from .models import Base
from .database import engine
from .routers import auth,todos,admin,users

app = FastAPI() # создание приложения FastAPI

Base.metadata.create_all(bind=engine) # создание всех таблиц в базе данных, определенных в моделях

@app.get('/healthy')
def healthy_check():
    return {"status":'healthy'}

app.include_router(auth.router) # добавляем пути к файлам ,что бы более структурировать файлы 
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)


