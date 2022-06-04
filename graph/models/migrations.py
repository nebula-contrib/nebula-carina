from graph.models.models import TagModel, EdgeTypeModel
from graph.ngql.connection import run_ngql
from graph.ngql.schema import show_tags, show_edges
from graph.settings import database_settings
from importlib import import_module
import inspect


def make_migrations():
    existing_tags = show_tags()
    existing_edges = show_edges()
    ngql_list = []
    model_paths = database_settings.model_paths
    for model_path in model_paths:
        module = import_module(model_path)
        for name, cls in module.__dict__.items():
            if inspect.isclass(cls) and (issubclass(cls, TagModel) or issubclass(cls, EdgeTypeModel)):
                if cls.db_name() in existing_tags:
                    alter_ngql = cls.alter_ngql()
                    alter_ngql and ngql_list.append(alter_ngql)
                elif cls.db_name() in existing_edges:
                    alter_ngql = cls.alter_ngql()
                    alter_ngql and ngql_list.append(alter_ngql)
                else:
                    ngql_list.append(cls.create_ngql())
    return ngql_list


def migrate(ngql_list):
    for ngql in ngql_list:
        run_ngql(ngql)
