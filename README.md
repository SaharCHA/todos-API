# Todos API

A RESTful Todo application API built with FastAPI, SQLAlchemy, PostgreSQL, and JWT authentication. It supports user registration and login, personal todo management, profile updates, and administrator-only todo operations.

## Features

- User registration and login
- Password hashing with bcrypt
- JWT bearer authentication with 20-minute access tokens
- CRUD operations for todos owned by the authenticated user
- User profile and phone-number management
- Password change with the current password
- Administrator access to all todos and todo deletion
- Automatic interactive API documentation through Swagger UI and ReDoc
- SQLAlchemy models and Alembic migration support
- One-command Docker Compose setup (API + PostgreSQL)
- pytest test coverage for authentication, users, todos, and admin routes

## Technology Stack

- [FastAPI](https://fastapi.tiangolo.com/) — API framework
- [SQLAlchemy](https://www.sqlalchemy.org/) — database ORM
- [PostgreSQL](https://www.postgresql.org/) — application database
- [psycopg2](https://www.psycopg.org/) — PostgreSQL driver
- [Alembic](https://alembic.sqlalchemy.org/) — database migrations
- [python-jose](https://python-jose.readthedocs.io/) — JWT handling
- [Passlib](https://passlib.readthedocs.io/) — password hashing
- [pytest](https://docs.pytest.org/) — automated testing
- [Uvicorn](https://www.uvicorn.org/) — ASGI server
- [Docker](https://www.docker.com/) and Docker Compose — containerized deployment

## Project Structure

```text
.
├── TodoApp/
│   ├── main.py                 # FastAPI application and router registration
│   ├── database.py             # SQLAlchemy engine and database session
│   ├── models.py               # Users and Todos database models
│   ├── alembic.ini             # Alembic configuration
│   └── routers/
│       ├── auth.py             # Registration, login, and JWT handling
│       ├── todos.py            # User todo CRUD routes
│       ├── users.py            # Profile and account routes
│       └── admin.py            # Administrator routes
├── test/                       # pytest suite and test database
├── Dockerfile                  # API image definition
├── docker-compose.yml          # API + PostgreSQL services
├── .dockerignore               # Files excluded from the Docker build context
├── .env.example                # Template for environment variables
└── requirements.txt            # Python dependencies
```

## Quick Start with Docker

The easiest way to run the project is with Docker Compose. It starts PostgreSQL and the API together, with no local Python or database setup.

**Prerequisites:** Docker with the Compose plugin (Docker Desktop includes both).

1. Clone the repository and enter the project directory:

   ```bash
   git clone https://github.com/SaharCHA/todos-API.git
   cd todos-API
   ```

2. (Recommended) Create your environment file and set your own secrets:

   ```bash
   cp .env.example .env
   ```

3. Build and start the stack:

   ```bash
   docker compose up --build
   ```

   Add `-d` to run it in the background.

The API is then available at <http://localhost:8000> (Swagger UI at <http://localhost:8000/docs>).

Useful commands:

```bash
docker compose logs -f api   # follow API logs
docker compose down          # stop and remove containers (data is kept)
docker compose down -v       # also delete the database volume
```

### Environment variables

| Variable | Description | Default |
|---|---|---|
| `POSTGRES_USER` | PostgreSQL user | `postgres` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `3026` |
| `POSTGRES_DB` | PostgreSQL database name | `TodoApplicationDatabase` |
| `SECRET_KEY` | JWT signing key | built-in development key |
| `DATABASE_URL` | Full SQLAlchemy URL (set automatically by Compose) | `postgresql://postgres:3026@localhost/TodoApplicationDatabase` |

> The defaults are for local development only. Set your own `POSTGRES_PASSWORD` and `SECRET_KEY` in `.env` before deploying anywhere else.

Tables are created automatically on startup, and database data is persisted in the `pgdata` Docker volume. Alembic migrations are not run in the container: on a fresh database the tables are already created from the models.

## Manual Setup (without Docker)

### Prerequisites

- Python 3.10 or newer
- PostgreSQL
- `pip`
- A virtual-environment tool such as `venv`

### Installation

1. Clone the repository and enter the project directory:

   ```bash
   git clone https://github.com/SaharCHA/todos-API.git
   cd todos-API
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

   On Windows PowerShell, activate it with:

   ```powershell
   venv\Scripts\Activate.ps1
   ```

3. Install the dependencies:

   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

### Database Configuration

Create a PostgreSQL database, for example:

```sql
CREATE DATABASE TodoApplicationDatabase;
```

Set the database URL with the `DATABASE_URL` environment variable (the default is defined in [TodoApp/database.py](TodoApp/database.py)):

```bash
export DATABASE_URL="postgresql://USER:PASSWORD@localhost/TodoApplicationDatabase"
```

Optionally set a custom JWT signing key:

```bash
export SECRET_KEY="a-long-random-string"
```

The Alembic configuration in [TodoApp/alembic.ini](TodoApp/alembic.ini) is separate and must be edited to use the same database URL.

> Keep real credentials out of source control.

When the application starts, SQLAlchemy creates any tables declared in [TodoApp/models.py](TodoApp/models.py) that do not already exist.

To run Alembic migrations from the repository root:

```bash
alembic -c TodoApp/alembic.ini upgrade head
```

### Running the API

From the repository root, start the development server with:

```bash
uvicorn TodoApp.main:app --reload
```

The API is available at <http://127.0.0.1:8000>.

| Interface | URL |
|---|---|
| Health check | http://127.0.0.1:8000/healthy |
| Swagger UI | http://127.0.0.1:8000/docs |
| ReDoc | http://127.0.0.1:8000/redoc |
| OpenAPI JSON | http://127.0.0.1:8000/openapi.json |

## API Overview

### Authentication

| Method | Path | Description | Authentication |
|---|---|---|---|
| `POST` | `/auth/` | Register a user | No |
| `POST` | `/auth/token` | Obtain a bearer token | No |
| `GET` | `/auth/get_all_users/` | List registered users | No |

The login endpoint uses OAuth2 password form fields:

- `username`
- `password`

Send the returned token in protected requests:

```text
Authorization: Bearer <access_token>
```

### Todos

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | List the current user's todos |
| `GET` | `/todo/{todo_id}` | Get one of the current user's todos |
| `POST` | `/todo` | Create a todo |
| `PUT` | `/todo/{todo_id}` | Update a todo |
| `DELETE` | `/todo/{todo_id}` | Delete a todo |

Todo creation and update requests use this JSON shape:

```json
{
  "title": "Learn FastAPI",
  "description": "Complete the API tutorial",
  "priority": 3,
  "complete": false
}
```

Validation rules:

- Title: at least 3 characters
- Description: between 3 and 100 characters
- Priority: greater than 0 and less than 6

### User Account

| Method | Path | Description | Request format |
|---|---|---|---|
| `GET` | `/users/get_user` | Get the current user | Bearer token |
| `PUT` | `/users/change_password` | Change the password | Form fields: `old_password`, `new_password` |
| `PUT` | `/users/change_number` | Update the phone number | Form field: `new_phone_number` |

### Administration

Administrator routes require a user whose JWT role is `admin`.

| Method | Path | Description |
|---|---|---|
| `GET` | `/admin/todo` | List every user's todos |
| `DELETE` | `/admin/todo/{todo_id}` | Delete any todo |

## Running Tests

Run the complete test suite from the repository root:

```bash
pytest
```

The tests use the SQLite database configured in [test/utils.py](test/utils.py), so they do not require PostgreSQL to execute the test fixtures. Override dependencies are applied in the individual test modules to isolate database and authentication behavior.

## Security Notes

- Set a unique `SECRET_KEY` before deploying the application.
- Use a sufficiently strong and confidential database password.
- Do not expose PostgreSQL credentials in commits or logs.
- Add server-side authorization checks consistently to user and administrator endpoints.
- Always provide `DATABASE_URL`, `POSTGRES_PASSWORD`, and `SECRET_KEY` through environment variables or a secrets manager; never rely on the built-in defaults outside local development.
