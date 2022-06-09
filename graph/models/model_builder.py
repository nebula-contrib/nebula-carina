from typing import Type

from graph.models.models import NebulaRecordModel
# MATCH (v) RETURN v LIMIT 3;
# MATCH (v:player) RETURN v LIMIT 3;
# MATCH (v:player:actor) RETURN v LIMIT 10;
# MATCH (v:player{name:"Tim Duncan"}) RETURN v;
# MATCH (v:player) WHERE v.player.name == "Tim Duncan" RETURN v;
# MATCH (v) WHERE id(v) == 'player101' RETURN v;
# MATCH (v:player { name: 'Tim Duncan' })--(v2) WHERE id(v2) IN ["player101", "player102"] RETURN v2;
# MATCH (v:player{name:"Tim Duncan"})--(v2:player) RETURN v2.player.name AS Name;
# MATCH (v:player{name:"Tim Duncan"})-->(v2:player) RETURN v2.player.name AS Name;
# MATCH (v:player{name:"Tim Duncan"})-->(v2)<--(v3) RETURN v3.player.name AS Name;
# MATCH ()-[e:follow]->() RETURN e limit 3;
# MATCH (v:player{name:"Tim Duncan"})-[e:follow{degree:95}]->(v2) RETURN e;
# MATCH (v:player{name:"Tim Duncan"})-[e:follow|:serve]->(v2) RETURN e;
# MATCH (v:player{name:"Tim Duncan"})-[]->(v2)<-[e:serve]-(v3) RETURN v2, v3;
from graph.ngql.query import match, OrderBy, Limit


class ModelBuilder(object):
    @staticmethod
    def match(pattern: str, to_model_dict: dict[str, Type[NebulaRecordModel]],
              *,
              condition: str = None, order_by: OrderBy = None, limit: Limit = None):
        results = match(pattern, ', '.join(to_model_dict.keys()), condition, order_by, limit)
        return [
            {
                key: to_model_dict[key].from_raw(value.value)
                for key, value in zip(results.keys(), row.values) if key in to_model_dict
            } for row in results.rows()
        ]
