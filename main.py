from fastapi import FastAPI

from example.models import Figure
from graph.models.migrations import make_migrations, migrate
from graph.ngql.space import *
from graph.ngql.schema import *
from graph.ngql.data_types import *
app = FastAPI()


@app.get("/")
async def root():
    # run_ngql('SHOW SPACES;')
    # print(show_spaces())
    # print(use_space('main'))
    # result = create_space('main', VidTypeEnum.INT64)
    # print(result)
    # if result.error_code() < 0:
    #     print(result.error_msg())
    f = Figure(vid=1000, name='xxx', age=22)
    # print(Figure._construct_tag())
    # run_ngql(Figure._construct_tag())
    # migrations = make_migrations()
    # print(migrations)
    # migrate(migrations)
    return f


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
