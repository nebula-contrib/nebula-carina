import time
import unittest

from nebula_carina.ngql.connection.connection import run_ngql
from nebula_carina.ngql.errors import NGqlError
from nebula_carina.ngql.schema.data_types import FixedString
from nebula_carina.ngql.schema.schema import create_schema_ngql, describe_tag
from nebula_carina.ngql.schema.space import show_spaces, create_space, VidTypeEnum, drop_space, use_space, \
    describe_space, make_vid_desc_string, clear_space
from nebula_carina.ngql.statements.schema import SchemaType, SchemaField


class TestSpace(unittest.TestCase):
    def test_spaces(self):
        spaces = [
            ('test_int', VidTypeEnum.INT64, {}, None),
            ('test_str', (VidTypeEnum.FIXED_STRING, 32), {}, None),
            ('test_中文名', 'FIXED_STRING(12)', {}, None),
            ('test!???', (VidTypeEnum.FIXED_STRING, 12), {}, NGqlError),
            ('test_exists', VidTypeEnum.INT64, {}, None),
            ('test_exists', VidTypeEnum.INT64, {}, None),
            ('test_exists', VidTypeEnum.INT64, {'if_not_exists': False}, NGqlError),
            ('test_partitions', VidTypeEnum.INT64, {'partition_num': 20}, None),
            ('test_replicas', VidTypeEnum.INT64, {'replica_factor': 3}, None),
            ('test_comments', VidTypeEnum.INT64, {'comment': '这个数据库不知道干什么用的。'}, None),
        ]
        for space_name, vid_type, kwargs, exception in spaces:
            if exception:
                with self.assertRaises(exception):
                    create_space(space_name, vid_type, **kwargs)
                continue
            else:
                create_space(space_name, vid_type, **kwargs)

            self.assertIn(space_name, show_spaces())
            result = describe_space(space_name)
            self.assertEqual(result['Partition Number'], kwargs.get('partition_num', 100))
            self.assertEqual(result['Replica Factor'], kwargs.get('replica_factor', 1))
            self.assertEqual(result['Comment'], kwargs.get('comment'))
            self.assertEqual(result['Vid Type'], make_vid_desc_string(vid_type))
        for space_name, vid_type, kwargs, exception in spaces:
            if not exception:
                drop_space(space_name)
                self.assertNotIn(space_name, show_spaces())

    def test_clear_space(self):
        space_name = 'test_clear'
        create_space(space_name, VidTypeEnum.INT64)
        self.assertIn(space_name, show_spaces())
        time.sleep(10)  # need 1 heartbeat
        use_space(space_name)
        tag_name = "test_tag_on_space_clean"
        run_ngql(create_schema_ngql(
            SchemaType.TAG, tag_name, [SchemaField('random_prop', FixedString(20))]
        ))
        des1 = describe_tag(tag_name)
        self.assertEqual(len(des1), 1)
        clear_space(space_name)
        self.assertEqual(des1, describe_tag(tag_name))
        drop_space(space_name)
        with self.assertRaises(NGqlError):
            describe_tag(tag_name)
