Fullstack application of https://udemy.com/course/fastapi-the-complete-course/

- Change some little things like a dependency file (New)
- Middleware log for any request (also have the process time of each request) using a Queue handler [handler from https://www.youtube.com/@mCoding].
- Using new way of declaring the tables (SQLAlchemy 2.0) and use `select`, `delete` and `update` to query, delete and update data.

Python3.12+

# How to use

First clone this repo!

```shell
    git clone https://github.com/aleamar264/fastapi_1.git
```

After that, use poetry to install all the dependency necessary with

```shell
    poetry install
```

and change folder to `project4` and run the services

```shell
    cd app/app/project4
    uvicorn main:app --reload
```

This will run in localhost with port 8000
