import datetime
import time
from collections import OrderedDict

import pytz

from nebula_carina.ngql.connection.connection import run_ngql
from nebula_carina.ngql.query.conditions import RawCondition
from nebula_carina.ngql.query.match import match
from nebula_carina.ngql.record.vertex import insert_vertex_ngql, update_vertex_ngql
from nebula_carina.ngql.schema import data_types
from nebula_carina.ngql.schema.schema import create_tag_ngql
from nebula_carina.ngql.schema.space import use_space
from nebula_carina.ngql.statements.clauses import Limit
from nebula_carina.ngql.statements.schema import SchemaField, Ttl
from nebula_carina.settings import database_settings
from nebula_carina.utils.utils import read_str
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
            ttl_definition=Ttl(0, 'ttl')
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
        time.sleep(20)  # wait for a heart beat

        # play with vertex
        tags = OrderedDict()
        tags['tag1'] = ['test_int', 'test_string', 'test_datetime', 'ttl']
        tags['tag2'] = ['test_fix_string', 'test_bool', 'test_date', 'test_time']
        current_date = datetime.datetime.now().date()
        tz = pytz.timezone(database_settings.timezone_name)
        prop_values_dict = {
            'vertex1': [
                data_types.Int16.value2db_str(32767),
                data_types.String.value2db_str("I'm a long string!" * 100),
                data_types.Datetime.value2db_str(data_types.Datetime.auto),
                data_types.Int64.value2db_str(291901),
                data_types.FixedString.value2db_str("I'm short"),
                data_types.Bool.value2db_str(False),
                data_types.Date.value2db_str(datetime.date(2000, 1, 1)),
                data_types.Time.value2db_str(datetime.time(3, 20, 3, 291, tzinfo=tz))
            ],
            'vertex2': [
                data_types.Int16.value2db_str(-222),
                data_types.String.value2db_str(''),
                data_types.Datetime.value2db_str(datetime.datetime(2025, 3, 23, 18,29, 1, 190, tzinfo=tz)),
                data_types.Int64.value2db_str(1.1529215e18),
                data_types.FixedString.value2db_str(''),
                data_types.Bool.value2db_str(True),
                data_types.Date.value2db_str(current_date),
                data_types.Time.value2db_str(datetime.time(1, 1, 1, 1, tzinfo=tz))
            ],
        }
        run_ngql(insert_vertex_ngql(tags, prop_values_dict))
        current_datetime = datetime.datetime.now(tz=tz)
        time.sleep(1)
        res = match('(v)', 'v', limit=Limit(5))
        v = res.column_values('v')[0].get_value().value
        self.assertEqual(read_str(v.vid.value), 'vertex1')
        self.assertEqual(len(v.tags), 2)
        for tag in v.tags:
            if read_str(tag.name) == 'tag2':
                self.assertFalse(data_types.Bool.ttype2python_type(tag.props[b'test_bool'].value))
                self.assertEqual(
                    data_types.Date.ttype2python_type(tag.props[b'test_date'].value), datetime.date(2000, 1, 1)
                )
                self.assertEqual(data_types.Time.ttype2python_type(
                    tag.props[b'test_time'].value), datetime.time(3, 20, 3, 291, tzinfo=tz)
                )
                self.assertEqual(
                    data_types.FixedString.ttype2python_type(tag.props[b'test_fix_string'].value), "I'm short"
                )
            elif read_str(tag.name) == 'tag1':
                self.assertEqual(
                    data_types.Int16.ttype2python_type(tag.props[b'test_int'].value), 32767
                )
                self.assertEqual(
                    data_types.String.ttype2python_type(tag.props[b'test_string'].value), "I'm a long string!" * 100
                )
                self.assertAlmostEqual(
                    data_types.Datetime.ttype2python_type(tag.props[b'test_datetime'].value), current_datetime,
                    delta=datetime.timedelta(seconds=3)
                )
                self.assertEqual(
                    data_types.Int64.ttype2python_type(tag.props[b'ttl'].value), 291901
                )
        v = res.column_values('v')[1].get_value().value
        self.assertEqual(read_str(v.vid.value), 'vertex2')
        self.assertEqual(len(v.tags), 2)
        for tag in v.tags:
            if read_str(tag.name) == 'tag2':
                self.assertTrue(data_types.Bool.ttype2python_type(tag.props[b'test_bool'].value))
                self.assertEqual(
                    data_types.Date.ttype2python_type(tag.props[b'test_date'].value), current_date
                )
                self.assertEqual(data_types.Time.ttype2python_type(
                    tag.props[b'test_time'].value), datetime.time(1, 1, 1, 1, tzinfo=tz)
                )
                self.assertEqual(
                    data_types.FixedString.ttype2python_type(tag.props[b'test_fix_string'].value), ""
                )
            elif read_str(tag.name) == 'tag1':
                self.assertEqual(
                    data_types.Int16.ttype2python_type(tag.props[b'test_int'].value), -222
                )
                self.assertEqual(
                    data_types.String.ttype2python_type(tag.props[b'test_string'].value), ''
                )
                self.assertEqual(
                    data_types.Datetime.ttype2python_type(tag.props[b'test_datetime'].value),
                    datetime.datetime(2025, 3, 23, 18, 29, 1, 190, tzinfo=tz)
                )
                self.assertEqual(
                    data_types.Int64.ttype2python_type(tag.props[b'ttl'].value), 1.1529215e18
                )

        # update_vertex_ngql
        next_now = data_types.Datetime.value2db_str(datetime.datetime.now(tz=tz))
        run_ngql(update_vertex_ngql('tag1', 'vertex1', {
            'test_int': data_types.Int16.value2db_str(122),
            'test_datetime': next_now
        }))
        res = match('(v: tag1)', 'v', RawCondition('id(v) == "vertex1"'))
        v = res.column_values('v')[0].get_value().value
        self.assertEqual(read_str(v.vid.value), 'vertex1')
        self.assertEqual(len(v.tags), 2)
        for tag in v.tags:
            if read_str(tag.name) == 'tag1':
                self.assertEqual(
                    data_types.Int16.ttype2python_type(tag.props[b'test_int'].value), 122
                )
                self.assertEqual(
                    data_types.String.ttype2python_type(tag.props[b'test_string'].value), "I'm a long string!" * 100
                )
                self.assertEqual(
                    data_types.Datetime.ttype2python_type(tag.props[b'test_datetime'].value), next_now
                )
                self.assertEqual(
                    data_types.Int64.ttype2python_type(tag.props[b'ttl'].value), 291901
                )
        # update_vertex_ngql  with condition
        # update_vertex_ngql yield output
        # upsert_vertex_ngql  (with condition  yield output)
        # delete_tag_ngql
        # delete_tag_ngql  (all tags deleted)
        # delete_vertex_ngql    (with edge)
        pass
