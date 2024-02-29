### Data validation

_Path validation_:

- Is to make validation for the values that enter using the _url path_.

```python
from fastapi import Path

@pp.get("/some/path/{id}")
async def some_fn(id: int = Path(gt=0)):
    ...
```

In this example, when we put some value less than 0, we get a error.

```json
{
  "detail": [
    {
      "type": "greater_than",
      "loc": ["path", "id"],
      "msg": "Input should be greater than 0",
      "input": "0",
      "ctx": {
        "gt": 0
      },
      "url": "https://errors.pydantic.dev/2.5/v/greater_than"
    }
  ]
}
```

We can make several configuration in this part depending of what is the logic in the function.

_Query validation_:

- Is to make validation for the values that enter using the _url query_.

```python
from fastapi import Query

@pp.get("/some/path/")
async def some_fn(published_date: int = Query(gt=0)):
    ...
```

```json
{
  "detail": [
    {
      "type": "less_than",
      "loc": ["query", "published_date"],
      "msg": "Input should be less than 2031",
      "input": "2100",
      "ctx": {
        "lt": 2031
      },
      "url": "https://errors.pydantic.dev/2.5/v/less_than"
    }
  ]
}
```

## SQLAlchemy

Now the `db.query` is legacy, in this moment we use select.

```python
from sqlalchemy import select

@app.get("/")
async def read(db: Annotated[Session, Depends(get_db)]):
  stmt = select(Model)
  return db.execute(stmt).scalars().all()
```

What is `Depends`? A way to declare thing that are required for the application/function to work by injecting the dependencies.

### Models

```python
from database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Boolean, String, ForeignKey
from sqlalchemy.ext.declarative import declared_attr

class NameMixin:
    @declared_attr.directive
    def __tablename__(cls)->str:
        return cls.__name__.lower()


class Todos(Base, NameMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String)
    priority: Mapped[int] = mapped_column(Integer)
    complete: Mapped[bool] = mapped_column(Boolean, default=False)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))

class Users(Base, NameMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True,
                                    index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String(20), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[str] = mapped_column(String)
```

### Schemas

```python
class GeneralPassword(BaseModel):
    password: str

class UserModel(BaseModel):
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    role: str

class CreateUserRequest(GeneralPassword, UserModel):
    ...

class AdminReturnUser(UserModel):
    is_active: bool
    id: int
    hashed_password: str


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool

    class Config:
        json_schema_extra = {
            "example": {
                "title" : "Todo title",
                "description": "Description of todo",
                "priority": 3,
                "complete": True
            }
        }
```

### Routers

## Authentication

### Hashing password

To save the password in a safe way, we need to hash the password, to do that, we can use the library `passlib` and `bcrypt`.

```shell
pip install passlib bcrypt
```

### Security in redocs

```python
from fastapi.security import OAuth2PasswordRequestForm
```

```python
def authenticated_user(username: str, password: str, db):
    stmt = select(Users).filter(Users.username == username)
    user = db.execute(stmt).scalar_one_or_none()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return True
```

### JWT (JSON Web Token)

Is a self-contained way to securely transmit data and information between two parties using a JSON object, also each JWT can be trusted because can be digitally signed.

```shell
openssl rand -hex 32
```

```python
# Create a JWT
def create_access_token(username: str, user_id: int, expire_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expire =  datetime.utcnow() + expire_delta
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET, algorithm=ALGORITHM)

```

To access to current user we need to create a function that can handle the JWT token by `OAuthPasswordBearer`, this access to the route `auth/token`.

```python
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')
        return {"username": username, 'id': user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')
```

The route that create the JWT token

```python
@router.post("/token", response_model=Token)
async def login_for_access_token(form: form_data, db: db_dependency):
    user = authenticated_user(form.username, form.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')
    token = create_access_token(user.username, user.id, timedelta(minutes=20))
    return JSONResponse({"access_token": token, "token_type": 'bearer'},
                        status_code=200)
```

To add security to one endpoint we need to create a dependency for this

```python
user_dependency = Annotated[dict, Depends(get_current_user)]

# Add dependency to endpoint

@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency,
                      db: db_dependency,
                      body: TodoRequest):
  if user is None:
      raise HTTPException(status_code=401, detail="Authentication failed")
  todo_model = Todos(**body.model_dump(), owner_id=user.get('id') )
  db.add(todo_model)
  db.commit()
```

## Middlewares

### Logs

In a new file called middlewares we create an async function which handle
all the http request a get the method, path and time in process this request.

```python
from fastapi import Request
from tools.logger import logger
import time


async def log_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start

    log_dict = {
        "url": request.url.path,
        "method": request.method,
        "process_time": process_time,
    }
    logger.info(log_dict, extra=log_dict)
    return response

```

In the main app we need to import from `starlette` the middleware `BaseHTTPMiddleware`.

```python
from tools.middleware import log_middleware
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI()
app.add_middleware(BaseHTTPMiddleware, dispatch=log_middleware)
```

With this, each time that a HTTP is requested this will be saved in the folder `logs/app.log`,
for further debug.

## Migrations

### Alembic

What is Alembic? Is a lightweight database migration tool for when we use SQLAlchemy.
This allow us to plan, transfer and upgrade resources within databases.

Also allow to change a SQLAlchemy table after created this.

| Alembic command                 | Details                                 |
| ------------------------------- | --------------------------------------- |
| alembic init <folder name>      | Initialize a new, generic enviroment    |
| alembic revision -m "<message>" | Create a new revision of the enviroment |
| alembic upgrade <revision #>    | Run upgrade on our database             |
| alembic downgrade -1            | Run downgrade in our database           |

# Testing

Exist 3 types of testing:

- Manual
- Unit:
- Involve testing individual components or units of software in isolation from the rest of the application.
- Validate each unit of the software performs as designed.
- Integration:
- Focus on testing the interaction between differents units or components of the piece of software.
- Test multiple unit together.

To make test, we need to create a folder named `test` and inside create a file called `__init__.py`. All the test should be called with `test_`.

In the root folder we can run the test using:

```shell
pytest
```

To create a object can be reutilizable in all the test, we can use the propertie called `fixture`.

```python
@pytest.fixture
def default_emplyee():
  return Student('Jhon', 'Doe', 'Computer Science', 3)

def test_person_initialization(default_employee):
  assert default_employee.first_name == 'Jhon'
```

## Test FastApi

```python
from fastapi.testclient import TestClient
import main
from httpx import Response
from fastapi import status

client = TestClient(main.app)


def test_return_health_check():
    response: Response = client.get("/healthy")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "Healthy"}
```

```shell
pytest --disable-warnings
```

### Test dependency

To test dependecy in FastAPI and pytest, in a new file we need to create a SQLite dabatase (Only for testing), and override some functions which are the dependency of our app.

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from database import Base
SQLALCHEMY_URL = "sqlite:///./testdb.db"

engine = create_engine(
    SQLALCHEMY_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)
```

It's the same behavior for any database. After that create the override functions

```python
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    return {"username": "aleamar264", "id": 1, "role": "admin"}
```

And use the option from the app of FastAPI to override the dependency

```python
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user
```

and add this to the test client.

```python
client = TestClient(app)
```

With this config we can test the route for get all the database.

```python
def test_read_all_authenticated():
    response: Response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []
```
