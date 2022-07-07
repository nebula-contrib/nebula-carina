from datetime import datetime

from fastapi import FastAPI

from example.models import VirtualCharacterVertex, KillEdge, Kill, Figure, Source
from nebula_model.models.migrations import make_migrations, migrate
from nebula_model.models.model_builder import ModelBuilder
from nebula_model.ngql.connection.connection import run_ngql
from nebula_model.ngql.query.conditions import RawCondition, Q
from nebula_model.ngql.query.match import Limit
from nebula_model.ngql.record.edge import insert_edge_ngql
from nebula_model.ngql.statements.edge import EdgeValue

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

    # vertex = VirtualCharacterVertex(vid=118, figure=Figure(name='test3', age=100, is_virtual=False))
    # vertex.save()
    #
    # vertex = VirtualCharacterVertex(
    #     vid=119, figure=Figure(name='test4', age=100, is_virtual=False), source=Source(name='trytest4')
    # )
    # vertex.save()
    # print(run_ngql('MATCH (v) WHERE id(v) == 114 RETURN v'))
    # results = match('(v)', 'v', limit=Limit(50))
    # print(results)
    # VirtualCharacterVertex.objects.any()
    # run_ngql('UPDATE VERTEX ON figure 119 SET name = "卧槽", age=33;')
    # run_ngql(update_vertex_ngql('figure', 119, {'name':  "卧槽123", 'age': 40}))
    VirtualCharacterVertex(
        vid=201, figure=Figure(
            name='test4', age=100, is_virtual=False, some_dt=datetime(2021, 3, 3, 0, 0, 0, 12)
        ), source=Source(name='trytest4')
    ).save()
    # VirtualCharacterVertex.objects.get(119)
    # # NEED INDEX TO FIGURE OUT
    # insert_edge = insert_edge_ngql(
    #         'kill', ['way', 'times'],
    #         [
    #             EdgeValue(113, 119, ['knife', 3]),
    #             EdgeValue(115, 119, ['gun', 100])
    #         ]
    #     )
    # print(insert_edge)
    # run_ngql(insert_edge)
    # list(ModelBuilder.match('(v:figure{name: "trytest4"})', {'v': VirtualCharacterVertex}, limit=Limit(50)))
    # k = KillEdge(src_vid=112, dst_vid=113, ranking=0, kill=Kill(way='gun', times=20))
    # k.save()
    # list(ModelBuilder.match('() -[e]-> ()', {'e': KillEdge}, limit=Limit(50)))
    # print(list(ModelBuilder.match('(v)', {'v': VirtualCharacterVertex}, limit=Limit(10))))
    ModelBuilder.match(
        '(v)-[e:kill]->(v2)', {'v': VirtualCharacterVertex, 'e': KillEdge, 'v2': VirtualCharacterVertex},
        condition=RawCondition('id(v) == 112'),
    )
    return ModelBuilder.match(
        '(v)-[e:kill]->(v2)', {'v': VirtualCharacterVertex, 'e': KillEdge, 'v2': VirtualCharacterVertex},
        condition=(Q(v__id=112) | Q(v__id=113)),
    )
