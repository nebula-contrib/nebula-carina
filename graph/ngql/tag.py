from graph.ngql.connection import run_ngql


def show_tags() -> list[str]:
    return run_ngql('SHOW TAGS;').column_values('Name')


def describe_tag(name):
    result = run_ngql(f'DESCRIBE TAG {name};')
    return result
