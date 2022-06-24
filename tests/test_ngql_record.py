import datetime
from collections import OrderedDict

from nebula_model.ngql.connection.connection import run_ngql
from nebula_model.ngql.record.vertex import insert_vertex_ngql
from nebula_model.ngql.schema import data_types
from nebula_model.ngql.schema.schema import create_tag_ngql
from nebula_model.ngql.schema.space import use_space
from nebula_model.ngql.statements.schema import SchemaField, Ttl
from tests.base import TestWithNewSpace


class TestRecord(TestWithNewSpace):
    def test_vertex(self):
        use_space(self.test_int_space_name)
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

        # play with vertex
        tags = OrderedDict()
        tags['tag1'] = ['test_int', 'test_string', 'test_datetime', 'ttl']
        tags['tag2'] = ['test_fix_string', 'test_bool', 'test_date', 'test_time']
        prop_values_dict = {
            111: ['test1', 33, True, 'test1another'],
            112: ['test2', 15, False, 'test2another']
        }
        insert_vertex_ngql(tags, prop_values_dict)
