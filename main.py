from fastapi import FastAPI

from example.models import Figure
from graph.ngql.space import use_space, create_space, VidTypeEnum

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
    f = Figure(vid=1000, name='xxx')
    return f


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
