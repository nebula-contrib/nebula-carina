# nebula-model

This project is designed to provide an easy-to-use orm package for the Nebula Graph database for Python development, especially web application development.

Nebula Graph is a powerful graph database, the only graph database solution in the world that can accommodate hundreds of billions of vertices and trillions of edges and provide millisecond-level query latency.

The goals of this project include providing an object-oriented description of the database structure, concise Query statements, and JSONizable results. In particular, I used the pydantic library with the expectation that this library can be used in conjunction with the fastapi framework.

This project is based on the official package nebula-python https://github.com/vesoft-inc/nebula-python.

At present, the project has just started and is not stable yet, the code changes rapidly and the method is unstable.
If you have any ideas for improving this project, you are very welcome to contact me via issue or email.

## Requirements

* Python (3.10)
* nebula3-python (>=3.10)

## Installation

install using `pip`

    pip install nebula-model

## Configuration

Please configure environment variables.
```
nebula_servers=["192.168.1.10:9669"];
nebula_user_name=root;
nebula_password=1234;
nebula_max_connection_pool_size=10;
nebula_model_paths=["example.models"];
nebula_default_space=main;
nebula_timezone_name=UTC
```
## Example
