from fastapi import FastAPI

from graph.connection import run_ngql

app = FastAPI()


@app.get("/")
async def root():
    run_ngql('USE blog;')
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
