from fastapi import APIRouter,Depends,status
from pydantic import BaseModel 
from models import Users
from database import db_dependency
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from jose import jwt 
from datetime import timedelta,datetime,timezone




router = APIRouter()

SECRET_KEY = ''
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


    

class CreateUserRequest(BaseModel):
    username: str
    email:str
    first_name: str
    last_name:str
    password: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type : str


def authenticate_user(username:str,password:str,db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.heshed_password):
        return False
    return user

def create_access_token(username:str,user_id : int , expires_delta:timedelta):
    encode = {"sub":username,"id":user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp" : expires})
    return jwt.encode(encode,SECRET_KEY,    algorithm=ALGORITHM)

@router.post("/auth/",status_code=status.HTTP_201_CREATED)
async def create_user(create_user_request : CreateUserRequest ,db:db_dependency):
    create_user_model = Users(
        email = create_user_request.email,
        username = create_user_request.username,
        first_name = create_user_request.first_name,
        last_name = create_user_request.last_name,
        role = create_user_request.role,
        heshed_password = bcrypt_context.hash(create_user_request.password),
        is_active = True
    )

    db.add(create_user_model)
    db.commit()
    return create_user_model 

    

@router.get("/auth/get_all_users/")
async def get_all_users(db:db_dependency):
    return db.query(Users).all()


@router.post("/token",response_model=Token)
async def login_for_access_token(form_data :Annotated[OAuth2PasswordRequestForm,Depends()],
                                 db:db_dependency):
    user = authenticate_user(username= form_data.username,
                             password=form_data.password,
                             db= db)
    if not user:
        return "Failed auth"
    token = create_access_token(user.username,user.id,timedelta(minutes=20))
    return {'access_token':token,'token_type':'baerer'}