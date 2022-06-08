from collections import OrderedDict

from fastapi import FastAPI

from example.models import Figure, Source, VirtualCharacter
from graph.models.migrations import make_migrations, migrate
from graph.ngql.query import match, Limit
from graph.ngql.query_utils import Q
from graph.ngql.space import *
from graph.ngql.schema import *
from graph.ngql.data_types import *
from graph.ngql.vertex import insert_vertex_ngql

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
    # f = Figure(vid=1000, name='xxx', age=22)
    # print(Figure._construct_tag())
    # run_ngql(Figure._construct_tag())
    # migrations = make_migrations()
    # print(migrations)
    # migrate(migrations)
    # tags = OrderedDict()
    # tags['figure'] = ['name', 'age', 'is_virtual']
    # tags['source'] = ['name']
    # prop_values_dict = {
    #     111: ['test1', 33, True, 'test1another'],
    #     112: ['test2', 15, False, 'test2another']
    # }
    #
    # vertex_ngql = insert_vertex_ngql(
    #     tags, prop_values_dict
    # )

    # print(vertex_ngql)
    # run_ngql(vertex_ngql)

    # vertex = VirtualCharacter(vid=118, figure=Figure(name='test3', age=100, is_virtual=False))
    # vertex.save()
    #
    # vertex = VirtualCharacter(
    #     vid=119, figure=Figure(name='test4', age=100, is_virtual=False), source=Source(name='trytest4')
    # )
    # vertex.save()
    # print(run_ngql('MATCH (v) WHERE id(v) == 114 RETURN v'))
    results = match('(v)', 'v', limit=Limit(50))
    print(results)
    
    return {}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
