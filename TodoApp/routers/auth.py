from fastapi import APIRouter,Depends
from pydantic import BaseModel 
from models import Users
from database import db_dependency
router = APIRouter()



    

class CreateUserRequest(BaseModel):
    username: str
    email:str
    first_name: str
    last_name:str
    password: str
    role: str

@router.post("/auth/")
async def create_user(create_user_request : CreateUserRequest ,db:db_dependency):
    create_user_model = Users(
        email = create_user_request.email,
        username = create_user_request.username,
        first_name = create_user_request.first_name,
        last_name = create_user_request.last_name,
        role = create_user_request.role,
        heshed_password = create_user_request.password,
        is_active = True
    )

    db.add(create_user_model)
    db.commit()
    return create_user_model

    

@router.get("/auth/get_all_users/")
async def get_all_users(db:db_dependency):
    return db.query(Users).all()