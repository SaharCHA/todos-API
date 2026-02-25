from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from TodoApp.database import Base
from TodoApp.main import app
from fastapi.testclient import TestClient
from TodoApp.models import Todos,Users
from TodoApp.routers.auth import bcrypt_context
import pytest


SQALCHEMY_DATABASE_URL = 'sqlite:///./test.db'


engine = create_engine(
    SQALCHEMY_DATABASE_URL,
    connect_args={'check_same_thread' :False},
    poolclass= StaticPool
)

TestingSessionLocal = sessionmaker(autocommit = False,autoflush =False,bind=engine )

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {'username':'Ivan','id':1,'user_role':'admin'}

client = TestClient(app)

@pytest.fixture
def test_user():
    user = Users(
        email = "test@gmail.com",
        username = "test",
        first_name = "first_name_test",
        last_name = "last_name_test",
        hashed_password = bcrypt_context.hash('testpassword'),
        role = "admin",
        phone_number = '+38 123 456 7890'
    )
    db =TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as connection:
        connection.execute(text('DELETE FROM users'))
        connection.commit()


@pytest.fixture
def test_todo():
    todo = Todos(
        title = 'Learn to code!',
        description = 'Need to learn everyday',
        priority = 5,
        complete = False,
        owner_id = 1
    )
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield db 
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()