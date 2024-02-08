FROM python:3.12-alpine
RUN apk update && apk upgrade
RUN apk add curl

WORKDIR /home/app
RUN  pip install --upgrade pip
RUN pip install  psycopg2-binary asyncpg SQLAlchemy alembic fastapi "uvicorn[standard]"

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"
