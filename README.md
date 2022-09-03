# nebula-model

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

    pip install nebula-model

## Configuration

Please configure environment variables.
```
nebula_servers='["192.168.1.10:9669"]'
nebula_user_name=root
nebula_password=1234
nebula_max_connection_pool_size=10
nebula_model_paths='["example.models"]'
nebula_default_space=main
nebula_timezone_name=UTC
```

You can export by:
```
export nebula_model_paths='["example.models"]' nebula_password=1234 nebula_servers='["192.168.1.10:9669"]' nebula_user_name=root nebula_default_space=main
```

## Example
Ensure that the default space exists. You can create a default space by creating a script:
```python
from nebula_model.ngql.schema.space import create_space, show_spaces, VidTypeEnum

main_space_name = "main"

if main_space_name not in show_spaces():
    create_space(main_space_name, (VidTypeEnum.FIXED_STRING, 20))
```

### Define Models
Then, develop models defined in nebula_model_paths.

#### Schema Models
* An TagModel is used to define a nebula tag.
* An EdgeTypeModel is used to define a nebula edge type.

For example:
```python
from datetime import datetime

from nebula_model.models import models
from nebula_model.models.fields import create_nebula_field as _
from nebula_model.ngql.schema import data_types


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


class Kill(models.EdgeTypeModel):
    way: str = _(data_types.FixedString(10), ..., )
    times: int = _(data_types.Int8, ..., )



```

#### Data Models
* An VertexModel is used to define a nebula vertex.
* An EdgeModel is used to define a nebula edge.

```python
from typing import Optional
from nebula_model.models import models


class VirtualCharacter(models.VertexModel):
    figure: Figure
    source: Optional[Source]


class BelongEdge(models.EdgeModel):
    belong: Belong


class KillEdge(models.EdgeModel):
    kill: Kill
```

### Migrations
use `make_migrations` and `migrate` to synchronize the schema to current space.

```python
from nebula_model.models.migrations import make_migrations, migrate

make_migrations()

# you can print out the result and check it
# then, run migrate
migrate(make_migrations())
```

### Data Model Method
```python
# create/update vertex
VirtualCharacter(
    vid=201, figure=Figure(
        name='test4', age=100, is_virtual=False, some_dt=datetime(2021, 3, 3, 0, 0, 0, 12)
    ), source=Source(name='trytest4')
).save()

# get by id
VirtualCharacter.objects.get(119)

# create/update edge
k = KillEdge(src_vid=112, dst_vid=113, ranking=0, kill=Kill(way='gun', times=20))
k.save()
```

### Model Builder
```python
from nebula_model.ngql.query.conditions import Q
from nebula_model.models.model_builder import ModelBuilder
from nebula_model.ngql.query.match import Limit


ModelBuilder.match('(v)', {'v': VirtualCharacter}, limit=Limit(10))

ModelBuilder.match(
    '(v)-[e:kill]->(v2)', {'v': VirtualCharacter, 'e': KillEdge, 'v2': VirtualCharacter},
    condition=Q(v__id__in=[112, 113]),
)
```