#!/usr/bin/env python

from setuptools import setup
setup(
    name="relations-sql",
    version="0.1.0",
    package_dir = {'': 'lib'},
    py_modules = [
        'relations_sql',
        'relations_sql.query'
    ],
    install_requires=[]
)
