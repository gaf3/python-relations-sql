"""
Base SQL module for all of Relations
"""

import relations

class SQLError(Exception):
    """
    SQL Error class that captures the sql
    """

    def __init__(self, sql, message):
        self.sql = sql
        self.message = message
        super().__init__(self.message)


class SQL:
    """
    Base class for every SQL expression
    """

    sql = None  # The text for a query
    args = None # The args for interpolation

    def __init__(self, sql=None, args=None):

        self.sql = sql
        self.args = args or []

    def __len__(self):

        return 1 if self.sql else 0

    @staticmethod
    def split(column):
        """
        Splits column value into name and path
        """

        path = relations.Field.split(column)

        name = path.pop(0)

        return name, path

    def generate(self, **kwargs):
        """
        Generate the sql and args
        """
