import json
from collections import OrderedDict
from typing import Any, Union


def insert_vertex_ngql(
        tag_props: OrderedDict[str, list[str]],
        prop_values_dict: dict[Union[int, str], list[Any]],
        *, if_not_exists: bool = True,
) -> str:
    """
    tags = OrderedDict()
    tags['figure'] = ['name', 'age', 'is_virtual']
    tags['source'] = ['name']
    prop_values_dict = {
        111: ['test1', 33, True, 'test1another'],
        112: ['test2', 15, False, 'test2another']
    }
    vertex_ngql = insert_vertex_ngql(tags, prop_values_dict)
    :param tag_props: OrderedDict{tag_name: [prop_names]}
    :param prop_values_dict: {vid: [field_values]}
    :param if_not_exists:
    :return:
    """

    tag_def = ', '.join(
        f'{tag_prop_name} ({", ".join(field_names)})' for tag_prop_name, field_names in tag_props.items()
    )
    prop_def = ', '.join(
        f'{vid}: ({", ".join(json.dumps(prop_val) for prop_val in prop_values)})'
        for vid, prop_values in prop_values_dict.items()
    )

    return f'INSERT VERTEX{" IF NOT EXISTS" if if_not_exists else ""} ' \
           f'{tag_def} VALUES {prop_def};'


def update_vertex_ngql(
    tag_name: str, vid: str | int, prop_name2values: dict[str, Any], condition: str = None, output: str = None
):
    set_str = ', '.join(f'{name} = {json.dumps(val)}' for name, val in prop_name2values.items())
    return f'UPDATE VERTEX ON {tag_name} {json.dumps(vid)} SET {set_str}' \
           f'{f" WHEN {condition}" if condition else ""}{f"YIELD {output}" if output else ""};'


def upsert_vertex_ngql(
    tag_name: str, vid: str | int, prop_name2values: dict[str, Any], condition: str = None, output: str = None
):
    set_str = ', '.join(f'{name} = {json.dumps(val)}' for name, val in prop_name2values.items())
    return f'UPSERT VERTEX ON {tag_name} {json.dumps(vid)} SET {set_str}' \
           f'{f" WHEN {condition}" if condition else ""}{f"YIELD {output}" if output else ""};'
