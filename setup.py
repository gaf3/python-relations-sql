#!/usr/bin/env python

from setuptools import setup
setup(
    name="python-relations-sql",
    version="0.6.5",
    package_dir = {'': 'lib'},
    py_modules = [
        'relations_sql',
        'relations_sql.sql',
        'relations_sql.expression',
        'relations_sql.criterion',
        'relations_sql.criteria',
        'relations_sql.clause',
        'relations_sql.query',
        'relations_sql.ddl',
        'relations_sql.column',
        'relations_sql.index',
        'relations_sql.table'
    ],
    install_requires=[]
)
