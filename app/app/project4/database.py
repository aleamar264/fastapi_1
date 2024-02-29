from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker, DeclarativeBase


# SQLALCHEMY_DATABASE_URL = "sqlite:///./todoapp.db"
url = URL.create(
    drivername="postgresql+psycopg2",
    username="postgres",
    password="postgres",
    host="127.0.0.1",
    database="Todos",
    port=5432,
)

engine = create_engine(url)
session_ = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass
