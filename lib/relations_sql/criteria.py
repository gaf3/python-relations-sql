"""
Module for CRITERIA
"""

import relations_sql


class CRITERIA(relations_sql.LIST):
    """
    Collection of CRITERIONS
    """

    ARGS = None
    KWARG = None
    KWARGS = None

    DELIMITTER = None
    PARENTHESES = True

    expressions = None

    def __init__(self, *args, **kwargs):

        self.expressions = []
        self(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        """
        Shorthand for add
        """
        self.add(*args, **kwargs)

    def add(self, *args, **kwargs):
        """
        Add expressiona
        """

        expressions = []

        if len(args) == 1 and isinstance(args[0], list):
            expressions.extend(args[0])
        else:
            expressions.extend(args)

        for expression in expressions:
            if isinstance(expression, relations_sql.SQL):
                self.expressions.append(expression)
            else:
                self.expressions.append(self.ARGS(expression))

        for key in sorted(kwargs.keys()):
            if self.KWARG is None or isinstance(kwargs[key], relations_sql.SQL):
                expression = kwargs[key]
            else:
                expression = self.KWARG(kwargs[key])
            self.expressions.append(self.KWARGS(key, expression))

    def generate(self):
        """
        Concats the values
        """

        sql = []
        self.sql = ""
        self.args = []

        if self:
            self.express(self.expressions, sql)
            self.sql = f"({self.DELIMITTER.join(sql)})" if self.PARENTHESES else self.DELIMITTER.join(sql)


class AND(CRITERIA):
    """
    CLAUSE for AND
    """

    ARGS = relations_sql.VALUE
    KWARGS = relations_sql.OP

    DELIMITTER = ' AND '


class OR(CRITERIA):
    """
    CLAUSE for OR
    """

    ARGS = relations_sql.VALUE
    KWARGS = relations_sql.OP

    DELIMITTER = ' OR '
