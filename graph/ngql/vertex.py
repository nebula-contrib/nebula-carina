from collections import OrderedDict
from typing import Any, Optional


def create_vertex_ngql(
        tag_props: OrderedDict[str, list[str]],
        prop_values_dict: dict[Optional[int, str], list[Any]],
        *, if_not_exists: bool = True,
) -> str:
    tag_def = ', '.join(
        f'{tag_prop_name} ({", ".join(field_names)})' for tag_prop_name, field_names in tag_props.items()
    )
    prop_def = ', '.join(
        f'{vid}: ({", ".join(prop_values)})' for vid, prop_values in prop_values_dict.items()
    )

    return f'CREATE VERTEX{" IF NOT EXISTS" if if_not_exists else ""} ' \
           f'{tag_def} VALUES {prop_def};'
