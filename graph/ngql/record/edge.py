from graph.ngql.statements.edge import EdgeValue


def insert_vertex_ngql(
        edge_type: str, prop_name_list: list[str],
        edge_values: list[EdgeValue],
        *, if_not_exists: bool = True,
) -> str:
    return f'INSERT EDGE{" IF NOT EXISTS" if if_not_exists else ""} ' \
           f'{edge_type} ({", ".join(prop_name_list)}) ' \
           f'VALUES {", ".join(str(edge_value) for edge_value in edge_values)};'
