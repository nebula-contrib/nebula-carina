import datetime

from nebula_carina.ngql.connection.connection import run_ngql
from nebula_carina.ngql.errors import NGqlError
from nebula_carina.ngql.schema import data_types
from nebula_carina.ngql.schema.schema import create_tag_ngql, describe_tag, show_tags, alter_tag_ngql, drop_tag_ngql, \
    alter_edge_ngql, describe_edge, drop_edge_ngql, show_edges, create_edge_ngql
from nebula_carina.ngql.schema.space import use_space
from nebula_carina.ngql.statements.schema import SchemaField, Ttl, Alter, AlterType
from tests.base import TestWithNewSpace


class TestSchema(TestWithNewSpace):
    def test_tag(self):
        use_space(self.test_int_space_name)
        tag_name = 'test_tag1'

        # ttl column not in
        with self.assertRaises(NGqlError):
            # Ttl column name not exist in columns
            run_ngql(create_tag_ngql(
                tag_name, [
                    SchemaField('noob_str', data_types.FixedString(10), nullable=False),
                ],
                ttl_definition=Ttl(300, 'ttl')
            ))

        with self.assertRaises(NGqlError):
            # Ttl column type illegal
            run_ngql(create_tag_ngql(
                tag_name, [
                    SchemaField('ttl', data_types.FixedString(10), nullable=False),
                ],
                ttl_definition=Ttl(300, 'ttl')
            ))

        schema_fields = [
            SchemaField('test_int', data_types.Int16()),
            SchemaField('test_string', data_types.String(), nullable=False, default='默认值', comment='备注1'),
            SchemaField('test_fix_string', data_types.FixedString(20), nullable=True, comment='备注2'),
            SchemaField('test_bool', data_types.Bool(), default=True),
            SchemaField('test_date', data_types.Date(), default=datetime.date(1999, 9, 9)),
            SchemaField('test_time', data_types.Time()),
            SchemaField('test_datetime', data_types.Datetime(), default=''),
            SchemaField('ttl', data_types.Int64()),
        ]
        tag_ngql = create_tag_ngql(
            tag_name, schema_fields,
            if_not_exists=True,
            ttl_definition=Ttl(3, 'ttl')
        )
        run_ngql(tag_ngql)
        self.assertIn(tag_name, show_tags())
        described_schema_fields = describe_tag(tag_name)
        self.assertEqual(schema_fields, described_schema_fields)

        to_add_properties = [
            SchemaField('test_add_small_int', data_types.Int8()),
            SchemaField('test_add_str', data_types.String())
        ]
        to_drop_property_names = ['test_int', 'test_bool']
        to_alter_properties = [
            SchemaField('test_date', data_types.Date(), default=datetime.date(2011, 1, 1)),
            SchemaField('test_fix_string', data_types.FixedString(30), comment='备注10086'),
        ]
        to_alter_property_dict = {p.prop_name: p for p in to_alter_properties}
        run_ngql(alter_tag_ngql(
            tag_name, alter_definitions=[
                Alter(AlterType.ADD, properties=to_add_properties),
                Alter(AlterType.DROP, prop_names=to_drop_property_names),
                Alter(AlterType.CHANGE, properties=to_alter_properties)
            ], ttl_definition=Ttl(5, 'ttl')
        ))
        described_schema_fields = describe_tag(tag_name)
        altered_schema = [
            (to_alter_property_dict[i.prop_name] if i.prop_name in to_alter_property_dict else i)
            for i in schema_fields + to_add_properties
            if i.prop_name not in to_drop_property_names
        ]
        self.assertEqual(altered_schema, described_schema_fields)
        run_ngql(drop_tag_ngql(tag_name))
        self.assertNotIn(tag_name, show_tags())

    def test_edge(self):
        use_space(self.test_string_space_name)
        edge_name = 'test_edge1'

        # ttl column not in
        with self.assertRaises(NGqlError):
            # Ttl column name not exist in columns
            run_ngql(create_edge_ngql(
                edge_name, [
                    SchemaField('noob_str', data_types.FixedString(10), nullable=False),
                ],
                ttl_definition=Ttl(300, 'ttl')
            ))

        with self.assertRaises(NGqlError):
            # Ttl column type illegal
            run_ngql(create_edge_ngql(
                edge_name, [
                    SchemaField('ttl', data_types.FixedString(10), nullable=False),
                ],
                ttl_definition=Ttl(300, 'ttl')
            ))

        schema_fields = [
            SchemaField('test_int', data_types.Int16()),
            SchemaField('test_string', data_types.String(), nullable=False, default='默认值', comment='备注1'),
            SchemaField('test_fix_string', data_types.FixedString(20), nullable=True, comment='备注2'),
            SchemaField('test_bool', data_types.Bool(), default=True),
            SchemaField('test_date', data_types.Date(), default=datetime.date(1999, 9, 9)),
            SchemaField('test_time', data_types.Time()),
            SchemaField('test_datetime', data_types.Datetime(), default=''),
            SchemaField('ttl', data_types.Int64()),
        ]
        edge_ngql = create_edge_ngql(
            edge_name, schema_fields,
            if_not_exists=True,
            ttl_definition=Ttl(3, 'ttl')
        )
        run_ngql(edge_ngql)
        self.assertIn(edge_name, show_edges())
        described_schema_fields = describe_edge(edge_name)
        self.assertEqual(schema_fields, described_schema_fields)

        to_add_properties = [
            SchemaField('test_add_small_int', data_types.Int8()),
            SchemaField('test_add_str', data_types.String())
        ]
        to_drop_property_names = ['test_int', 'test_bool']
        to_alter_properties = [
            SchemaField('test_date', data_types.Date(), default=datetime.date(2011, 1, 1)),
            SchemaField('test_fix_string', data_types.FixedString(30), comment='备注10086'),
        ]
        to_alter_property_dict = {p.prop_name: p for p in to_alter_properties}
        run_ngql(alter_edge_ngql(
            edge_name, alter_definitions=[
                Alter(AlterType.ADD, properties=to_add_properties),
                Alter(AlterType.DROP, prop_names=to_drop_property_names),
                Alter(AlterType.CHANGE, properties=to_alter_properties)
            ], ttl_definition=Ttl(5, 'ttl')
        ))
        described_schema_fields = describe_edge(edge_name)
        altered_schema = [
            (to_alter_property_dict[i.prop_name] if i.prop_name in to_alter_property_dict else i)
            for i in schema_fields + to_add_properties
            if i.prop_name not in to_drop_property_names
        ]
        self.assertEqual(altered_schema, described_schema_fields)
        run_ngql(drop_edge_ngql(edge_name))
        self.assertNotIn(edge_name, show_edges())
