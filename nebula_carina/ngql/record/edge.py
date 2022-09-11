from nebula_carina.ngql.statements.edge import EdgeValue, EdgeDefinition


def insert_edge_ngql(
        edge_type_name: str, prop_name_list: list[str],
        edge_values: list[EdgeValue],
        *, if_not_exists: bool = True,
) -> str:
    return f'INSERT EDGE{" IF NOT EXISTS" if if_not_exists else ""} ' \
           f'{edge_type_name} ({", ".join(prop_name_list)}) ' \
           f'VALUES {", ".join(str(edge_value) for edge_value in edge_values)};'


def delete_edge_ngql(edge_type_name: str, edge_definitions: list[EdgeDefinition]) -> str:
    return f'DELETE EDGE {edge_type_name} ' \
           f'{", ".join(str(edge_definition) for edge_definition in edge_definitions)};'


def update_edge_ngql(
        edge_type_name: str, edge_definition: EdgeDefinition,
        prop_name2values: dict[str, any], condition: str = None, output: str = None
):
    set_str = ', '.join(f'{name} = {val}' for name, val in prop_name2values.items())
    return f'UPDATE EDGE ON {edge_type_name} {edge_definition} SET {set_str}' \
           f'{f" WHEN {condition}" if condition else ""}{f"YIELD {output}" if output else ""};'


def upsert_edge_ngql(
        edge_type_name: str, edge_definition: EdgeDefinition,
        prop_name2values: dict[str, any], condition: str = None, output: str = None
):
    set_str = ', '.join(f'{name} = {val}' for name, val in prop_name2values.items())
    return f'UPSERT EDGE ON {edge_type_name} {edge_definition} SET {set_str}' \
           f'{f" WHEN {condition}" if condition else ""}{f"YIELD {output}" if output else ""};'
