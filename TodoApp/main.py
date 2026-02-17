from fastapi import  FastAPI
import models
from database import engine
from routers import auth,todos,admin,users

app = FastAPI() # создание приложения FastAPI

models.Base.metadata.create_all(bind=engine) # создание всех таблиц в базе данных, определенных в моделях

app.include_router(auth.router) # добавляем пути к файлам ,что бы более структурировать файлы 
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)


