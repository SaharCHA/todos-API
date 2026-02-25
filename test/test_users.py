from .utils import * 
from TodoApp.database import  get_db
from TodoApp.routers.auth import get_current_user
from fastapi import status

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_return_user(test_user):
    response = client.get("users/get_user")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['email'] == "test@gmail.com"
    assert response.json()['username'] == "test"
    assert response.json()['first_name'] == "first_name_test"
    assert response.json()['last_name'] == "last_name_test"
    assert response.json()['role'] == "admin"
    assert response.json()['phone_number'] == '+38 123 456 7890'

    

def test_change_password_success(test_user):
    response = client.put('/users/change_password',
                          data = {'old_password':'testpassword', 'new_password':'newpassword'})
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    password = db.query(Users).filter(Users.id == 1).first().hashed_password
    assert bcrypt_context.verify('newpassword', password)


def test_change_password_invalid_current_password(test_user):
    response = client.put('/users/change_password',
                          data = {'old_password':'invalidpassword', 'new_password':'newpassword'})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_change_number_success(test_user):
    response = client.put("/users/change_number",data = {'new_phone_number' : "+38 068 056 3467"})
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    check_number = db.query(Users).filter(Users.id == 1).first().phone_number
    assert check_number == "+38 068 056 3467"

def test_change_number_not_authenticated():
    app.dependency_overrides[get_current_user] = lambda:None
    response = client.put("/users/change_number",data = {'new_phone_number' : "+38 068 056 3467"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    app.dependency_overrides[get_current_user] = override_get_current_user

    