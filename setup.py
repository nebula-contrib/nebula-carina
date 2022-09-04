from setuptools import setup, find_packages
from pathlib import Path

base_dir = Path(__file__).parent
long_description = (base_dir / 'README.md').read_text()


setup(
    name='nebula-model',
    version='0.1.1',
    author='Sword Elucidator',
    author_email='nagisa940216@gmail.com',
    url='https://github.com/SwordElucidator/nebula-model',
    license='MIT Licence',
    description='Nebula Database Modeling powered by Pydantic and Nebula Python.',
    packages=find_packages(),
    package_dir={'nebula_model': 'nebula_model'},
    python_requires='>=3.10',
    install_requires=['nebula3-python', 'pydantic'],
)
