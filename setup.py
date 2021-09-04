#!/usr/bin/env python

from setuptools import setup
setup(
    name="relations-sql",
    version="0.3.0",
    package_dir = {'': 'lib'},
    py_modules = [
        'relations_sql',
        'relations_sql.sql',
        'relations_sql.expression',
        'relations_sql.criterion',
        'relations_sql.criteria',
        'relations_sql.clause',
        'relations_sql.query'
    ],
    install_requires=[]
)
