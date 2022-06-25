import datetime
import time
from collections import OrderedDict

from nebula_model.ngql.connection.connection import run_ngql
from nebula_model.ngql.query.match import match
from nebula_model.ngql.record.vertex import insert_vertex_ngql
from nebula_model.ngql.schema import data_types
from nebula_model.ngql.schema.schema import create_tag_ngql
from nebula_model.ngql.schema.space import use_space
from nebula_model.ngql.statements.clauses import Limit
from nebula_model.ngql.statements.schema import SchemaField, Ttl
from tests.base import TestWithNewSpace


class TestRecord(TestWithNewSpace):
    def test_vertex(self):
        use_space(self.test_string_space_name)
        # create tag
        tag_name1 = 'tag1'
        schema_fields1 = [
            SchemaField('test_int', data_types.Int16()),
            SchemaField('test_string', data_types.String(), nullable=False, default='默认值', comment='备注1'),
            SchemaField('test_datetime', data_types.Datetime(), default=''),
            SchemaField('ttl', data_types.Int64()),
        ]
        tag_ngql = create_tag_ngql(
            tag_name1, schema_fields1,
            if_not_exists=True,
            ttl_definition=Ttl(3, 'ttl')
        )
        run_ngql(tag_ngql)
        tag_name2 = 'tag2'
        schema_fields2 = [
            SchemaField('test_fix_string', data_types.FixedString(20), nullable=True, comment='备注2'),
            SchemaField('test_bool', data_types.Bool(), default=True),
            SchemaField('test_date', data_types.Date(), default=datetime.date(1999, 9, 9)),
            SchemaField('test_time', data_types.Time()),
        ]
        tag_ngql = create_tag_ngql(
            tag_name2, schema_fields2,
            if_not_exists=True,
        )
        run_ngql(tag_ngql)
        time.sleep(10)  # wait for a heart beat

        # play with vertex
        tags = OrderedDict()
        tags['tag1'] = ['test_int', 'test_string', 'test_datetime', 'ttl']
        tags['tag2'] = ['test_fix_string', 'test_bool', 'test_date', 'test_time']
        prop_values_dict = {
            'vertex1': [
                data_types.Int16.value2db_str(282919282),
                data_types.String.value2db_str("I'm a long string!" * 100),
                data_types.Datetime.value2db_str(data_types.Datetime.auto),
                data_types.Int64.value2db_str(291901),
                data_types.FixedString.value2db_str("I'm short"),
                data_types.Bool.value2db_str(False),
                data_types.Date.value2db_str(datetime.date(2000, 1, 1)),
                data_types.Time.value2db_str(datetime.time(3, 20, 3, 291))
            ],
            'vertex2': [
                data_types.Int16.value2db_str(-222),
                data_types.String.value2db_str(''),
                data_types.Datetime.value2db_str(datetime.datetime(2025, 3, 23, 18,29, 1, 190)),
                data_types.Int64.value2db_str(1.1529215e18),
                data_types.FixedString.value2db_str(None),
                data_types.Bool.value2db_str(None),
                data_types.Date.value2db_str(None),
                data_types.Time.value2db_str(datetime.time(1, 1, 1, 1))
            ],
        }
        run_ngql(insert_vertex_ngql(tags, prop_values_dict))
        res = match('(v)', 'v', limit=Limit(5))
        print(1)
        pass
