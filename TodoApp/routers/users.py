from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, HTTPException, Path,status,Form
from database import db_dependency
from models import Users
from .auth import get_current_user, authenticate_user,bcrypt_context


router = APIRouter(
    prefix = "/users",
    tags=["users"]
) # создание приложения FastAPI

user_dependency = Annotated[dict,Depends(get_current_user)]

@router.get("/get_user",status_code=status.HTTP_200_OK)
async def get_user(user:user_dependency,db:db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    if user_model is None:
        raise HTTPException(status_code=404,detail="User not found")
    return user_model

@router.put("/change_password",status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    user:user_dependency,
    db:db_dependency,
    old_password:str=Form(...),
    new_password:str=Form(...)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    user_check = authenticate_user(user.get('username'),old_password,db)
    if user is False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    user_model= db.query(Users).filter(Users.id == user.get('id')).first()
    user_model.heshed_password = bcrypt_context.hash(new_password)
    db.commit()
    
    
