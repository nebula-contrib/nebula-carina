# nebula-carina

This project is designed to provide an easy-to-use orm package for the Nebula Graph database for Python development, especially web application development.

Nebula Graph is a powerful graph database, the only graph database solution in the world that can accommodate hundreds of billions of vertices and trillions of edges and provide millisecond-level query latency.

The goals of this project include providing an object-oriented description of the database structure, concise Query statements, and JSONizable results. In particular, I used the pydantic library with the expectation that this library can be used in conjunction with the fastapi framework.

This project is based on the official package nebula-python https://github.com/vesoft-inc/nebula-python.

At present, the project has just started and is not stable yet, the code changes rapidly and the method is unstable.
If you have any ideas for improving this project, you are very welcome to contact me via issue or email.

## Requirements

* Python (3.10)
* nebula3-python (>=3.10)

## Installation

install using `pip`

    pip install nebula-carina

## Configuration

Please configure environment variables.
```
nebula_servers='["192.168.1.10:9669"]'
nebula_user_name=root
nebula_password=1234
nebula_max_connection_pool_size=10
nebula_carina_paths='["example.models"]'
nebula_default_space=main
nebula_auto_create_default_space_with_vid_desc=FIXED_STRING(20)
nebula_timezone_name=UTC
```

You can export by:
```
export nebula_carina_paths='["example.models"]' nebula_password=1234 nebula_servers='["192.168.1.10:9669"]' nebula_user_name=root nebula_default_space=main nebula_auto_create_default_space_with_vid_desc=FIXED_STRING(20)
```

## Example
Ensure that the default space exists. You can create a default space by creating a script:
```python
from nebula_carina.ngql.schema.space import create_space, show_spaces, VidTypeEnum

main_space_name = "main"

if main_space_name not in show_spaces():
    create_space(main_space_name, (VidTypeEnum.FIXED_STRING, 20))
```
Or you can just set `nebula_auto_create_default_space_with_vid_desc=FIXED_STRING(20)` so that it will be automatically handled.

### Define Models
Then, develop models defined in nebula_carina_paths.

#### Schema Models
* An TagModel is used to define a nebula tag.
* An EdgeTypeModel is used to define a nebula edge type.

For example:
```python
from datetime import datetime

from nebula_carina.models import models
from nebula_carina.models.fields import create_nebula_field as _
from nebula_carina.ngql.schema import data_types


class Figure(models.TagModel):
    name: str = _(data_types.FixedString(30), ..., )
    age: int = _(data_types.Int16, ..., )
    valid_until: int = _(data_types.Int64, None, )
    hp: int = _(data_types.Int16, 100, )
    style: str = _(data_types.FixedString(10), 'rap', )
    is_virtual: bool = _(data_types.Bool, True)
    created_on: datetime = _(data_types.Datetime, data_types.Datetime.auto)
    some_dt: datetime = _(data_types.Datetime, datetime(2022, 1, 1))

    class Meta:
        ttl_duration = 100
        ttl_col = 'valid_until'


class Source(models.TagModel):
    name: str = _(data_types.FixedString(30), ..., )


class Belong(models.EdgeTypeModel):
    pass


class Love(models.EdgeTypeModel):
    way: str = _(data_types.FixedString(10), ..., )
    times: int = _(data_types.Int8, ..., )

    
class Support(models.EdgeTypeModel):
    food_amount: int = _(data_types.Int16, ..., )
```

#### Data Models
* An VertexModel is used to define a nebula vertex. It does nothing to the schema.

```python
from nebula_carina.models import models


class VirtualCharacter(models.VertexModel):
    figure: Figure
    source: Source


class LimitedCharacter(models.VertexModel):
    figure: Figure
```

* An EdgeModel is used to define a nebula edge. But note that there will be no subclasses for edge model since we don't need it.

### Migrations
use `make_migrations` and `migrate` to synchronize the schema to current space.

```python
from nebula_carina.models.migrations import make_migrations, migrate

make_migrations()

# you can print out the result and check it
# then, run migrate
migrate(make_migrations())
```

### Data Model Method
```python
from example.models import VirtualCharacter, Figure, Source, LimitedCharacter, Love, Support
from nebula_carina.models.models import EdgeModel, Limit
from datetime import datetime


# create/update vertex
VirtualCharacter(
    vid='char_test1', figure=Figure(
        name='test1', age=100, is_virtual=False, some_dt=datetime(2021, 3, 3, 0, 0, 0, 12)
    ), source=Source(name='movie1')
).save()

VirtualCharacter(
    vid='char_test2', figure=Figure(
        name='test2', age=30, is_virtual=False, some_dt=datetime(2021, 3, 3, 0, 0, 0, 12)
    ), source=Source(name='movie2')
).save()

LimitedCharacter(
    vid='char_test3', figure=Figure(
        name='test3', age=200, is_virtual=True, some_dt=datetime(2022, 3, 3, 0, 0, 0, 12)
    )
).save()

# note that a VirtualCharacter could still be recognized as a LimitedCharacter, but a LimitedCharacter is not a VirtualCharacter

# create/update edge
EdgeModel(src_vid='char_test1', dst_vid='char_test2', ranking=0, edge_type=Love(way='gun', times=40)).save()
# create/update another edge
EdgeModel(src_vid='char_test1', dst_vid='char_test2', ranking=0, edge_type=Support(food_amount=400)).save()

# get vertex by id
character1 = VirtualCharacter.objects.get('char_test1')
character2 = VirtualCharacter.objects.get('char_test2')

# find the exact edge by src_vid, dst_vid and edge type
edge1 = EdgeModel.objects.get('char_test1', 'char_test2', Love)

# find all edges between vertexes
EdgeModel.objects.find_between('char_test1', 'char_test2', limit=Limit(10))
# find specific edges between vertexes
EdgeModel.objects.find_between('char_test1', 'char_test2', Support)

# find vertexes (sources) that go towards node by the specific edge type
VirtualCharacter.objects.find_sources('char_test2', Love, distinct=True, limit=Limit(1))
# Or just by any edge
VirtualCharacter.objects.find_sources('char_test2')
# or just
character2.get_sources(Love, VirtualCharacter)

# similarly, find the destinations
VirtualCharacter.objects.find_destinations('char_test1', Love)
# or
character1.get_destinations(Love, VirtualCharacter)

# out edges & reverse edges
character1.get_out_edges(Love)
character2.get_reverse_edges(Love)
# get edges & vertexes together
character1.get_out_edge_and_destinations(Love, VirtualCharacter)
character2.get_reverse_edge_and_sources(Love, VirtualCharacter)
```

### Model Builder
* A easy model builder ready for you to build any ngql
```python
from nebula_carina.ngql.query.conditions import Q
from nebula_carina.models.model_builder import ModelBuilder
from nebula_carina.ngql.query.match import Limit
from nebula_carina.models.models import EdgeModel


ModelBuilder.match('(v)', {'v': VirtualCharacter}, limit=Limit(10))

ModelBuilder.match(
    '(v)-[e:love]->(v2)', {'v': VirtualCharacter, 'e': EdgeModel, 'v2': VirtualCharacter},
    condition=Q(v__id__in=["char_test1", "char_test3"]),
)
```

### Fastapi
If you are using fastapi, then serialization and deserialization are already handled by the repo. For example, in your api functions, you are welcomed to use the result of data model or the model builder in your return function. It's very easy to use!
```python
from fastapi import FastAPI
from example.models import VirtualCharacter, Love
from nebula_carina.models.model_builder import ModelBuilder
from nebula_carina.models.models import EdgeModel
from nebula_carina.ngql.query.conditions import Q


app = FastAPI()


@app.get("/character/{character_id}")
async def get_character(character_id: str):
    return VirtualCharacter.objects.get(character_id)


@app.get("/character/{character_id}/admirers")
async def get_admirers(character_id: str):
    return VirtualCharacter.objects.find_sources(character_id, Love, distinct=True)


@app.get("/character/{character_id}/your-complex-relation")
async def what_a_complex_human_relation(character_id: str):
    return ModelBuilder.match(
        '(v)-[e:love]->(v2)-[e2:love]->(v3)', {
            'v': VirtualCharacter, 'e': EdgeModel, 'v2': VirtualCharacter,
            'e2': EdgeModel, 'v3': VirtualCharacter
        },
        condition=Q(v__id=character_id),
    )
```

## TODO List
- [ ] Indexes
- [ ] TTL on schema
- [ ] Go / Fetch / Lookup statements
- [x] Session / Connection Pool (partially, might implement a better one later base on nebula-python)
- [ ] More abstractions on different scenarios
- [ ] Default values for schema models
- [ ] Generic Vertex Model
- [ ] Django Support