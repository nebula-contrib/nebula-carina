import unittest

from nebula_model.ngql.errors import NGqlError
from nebula_model.ngql.schema.space import show_spaces, create_space, VidTypeEnum, drop_space, use_space, \
    describe_space, make_vid_desc_string
from tests.base import TestWithNewSpace


class TestSpace(unittest.TestCase):
    def test_spaces(self):
        spaces = [
            ('test_int', VidTypeEnum.INT64, {}, None),
            ('test_str', (VidTypeEnum.FIXED_STRING, 32), {}, None),
            ('test_中文名', (VidTypeEnum.FIXED_STRING, 12), {}, None),
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

            self.assertTrue(space_name in show_spaces())
            result = describe_space(space_name)
            self.assertEqual(result['Partition Number'], kwargs.get('partition_num', 100))
            self.assertEqual(result['Replica Factor'], kwargs.get('replica_factor', 1))
            self.assertEqual(result['Comment'], kwargs.get('Comment'))
            self.assertEqual(result['Vid Type'], make_vid_desc_string(vid_type))
            # TODO use_space   clear_space
        for space_name, vid_type, kwargs, exception in spaces:
            drop_space(space_name)
