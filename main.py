from datetime import datetime

from fastapi import FastAPI

from example.models import VirtualCharacter, Love, Figure, Source, Support, LimitedCharacter
from nebula_model.models.migrations import make_migrations, migrate
from nebula_model.models.model_builder import ModelBuilder
from nebula_model.models.models import EdgeModel
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

    # vertex = VirtualCharacter(vid=118, figure=Figure(name='test3', age=100, is_virtual=False))
    # vertex.save()
    #
    # vertex = VirtualCharacter(
    #     vid=119, figure=Figure(name='test4', age=100, is_virtual=False), source=Source(name='trytest4')
    # )
    # vertex.save()
    # print(run_ngql('MATCH (v) WHERE id(v) == 114 RETURN v'))
    # results = match('(v)', 'v', limit=Limit(50))
    # print(results)
    # VirtualCharacter.objects.any()
    # run_ngql('UPDATE VERTEX ON figure 119 SET name = "卧槽", age=33;')
    # run_ngql(update_vertex_ngql('figure', 119, {'name':  "卧槽123", 'age': 40}))
    # VirtualCharacter(
    #     vid=201, figure=Figure(
    #         name='test4', age=100, is_virtual=False, some_dt=datetime(2021, 3, 3, 0, 0, 0, 12)
    #     ), source=Source(name='trytest4')
    # ).save()
    # VirtualCharacter.objects.get(119)
    # # NEED INDEX TO FIGURE OUT
    # insert_edge = insert_edge_ngql(
    #         'love', ['way', 'times'],
    #         [
    #             EdgeValue(113, 119, ['knife', 3]),
    #             EdgeValue(115, 119, ['gun', 100])
    #         ]
    #     )
    # print(insert_edge)
    # run_ngql(insert_edge)
    # list(ModelBuilder.match('(v:figure{name: "trytest4"})', {'v': VirtualCharacter}, limit=Limit(50)))
    # k = KillEdge(src_vid=112, dst_vid=113, ranking=0, love=Love(way='gun', times=20))
    # k.save()
    # list(ModelBuilder.match('() -[e]-> ()', {'e': KillEdge}, limit=Limit(50)))
    # print(list(ModelBuilder.match('(v)', {'v': VirtualCharacter}, limit=Limit(10))))
    # ModelBuilder.match(
    #     '(v)-[e:love]->(v2)', {'v': VirtualCharacter, 'e': KillEdge, 'v2': VirtualCharacter},
    #     condition=(Q(v__id=112) | Q(v__id=113)),
    # )
    # v
    # VirtualCharacter()
    # N(VirtualCharacter) >> 2 << 3

    # scenario
    # VirtualCharacter(
    #     vid='char_test1', figure=Figure(
    #         name='test1', age=100, is_virtual=False, some_dt=datetime(2021, 3, 3, 0, 0, 0, 12)
    #     ), source=Source(name='movie1')
    # ).save()
    #
    # VirtualCharacter(
    #     vid='char_test2', figure=Figure(
    #         name='test2', age=30, is_virtual=False, some_dt=datetime(2021, 3, 3, 0, 0, 0, 12)
    #     ), source=Source(name='movie2')
    # ).save()
    # VirtualCharacter(
    #     vid='char_test3', figure=Figure(
    #         name='test3', age=200, is_virtual=True, some_dt=datetime(2022, 3, 3, 0, 0, 0, 12)
    #     ), source=Source(name='movie1')
    # ).save()
    # EdgeModel(src_vid='char_test1', dst_vid='char_test2', ranking=0, edge_type=Love(way='gun', times=40)).save()
    # return EdgeModel.objects.find_between('char_test1', 'char_test2')
    character1 = VirtualCharacter.objects.get('char_test1')
    character2 = VirtualCharacter.objects.get('char_test2')
    character1.get_out_edges(Love)
    character2.get_reverse_edges(Love)
    character1.get_out_edge_and_destinations(Love, VirtualCharacter)
    character2.get_reverse_edge_and_sources(Love, VirtualCharacter)
    # return VirtualCharacter.objects.find_destinations('char_test1', Love)
    # return VirtualCharacter.objects.find_sources('char_test2', Love, distinct=False, limit=Limit(1))
    # return character2.get_sources(Love, VirtualCharacter)
    return character1.get_destinations(Love, VirtualCharacter)
    # return rst
    # return ModelBuilder.match(
    #     '(v)-[e:love]->(v2)', {'v': VirtualCharacter, 'e': KillEdge, 'v2': VirtualCharacter},
    #     condition=Q(v__id__in=[112, 113]),
    # )
