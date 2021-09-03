"""
Module for CRITERIA
"""

import relations_sql


class CRITERIA(relations_sql.LIST):
    """
    Collection of CRITERIONS
    """

    ARGS = None

    DELIMITTER = None
    PARENTHESES = True

    expressions = None

    def __init__(self, *args):

        self.expressions = []
        self(*args)

    def __call__(self, *args):
        """
        Shorthand for add
        """
        self.add(*args)

    def add(self, *args):
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

    DELIMITTER = ' AND '


class OR(CRITERIA):
    """
    CLAUSE for OR
    """

    ARGS = relations_sql.VALUE

    DELIMITTER = ' OR '


class SETS(relations_sql.RANGES):
    """
    For comparing sets with each other
    """

    expression = None

    def generate(self):
        """
        Concats the values
        """

        self.expression.generate()
        self.sql = self.expression.sql
        self.args = self.expression.args

    def __len__(self):

        return 1


class HAS(SETS):
    """
    For if the left has all the members of right
    """

    CONTAINS = relations_sql.CONTAINS

    def __init__(self, left=None, right=None, jsonify=False, **kwargs):

        self.expression = self.CONTAINS(left, right, jsonify, **kwargs)


class NOTHAS(SETS):
    """
    For if the left doesn't all the members of right
    """

    NOT = relations_sql.NOT
    HAS = HAS

    def __init__(self, left=None, right=None, jsonify=False, **kwargs):

        self.expression = self.NOT(self.HAS(left, right, jsonify=jsonify, **kwargs))


class ANY(SETS):
    """
    For if the left has any the members of right
    """

    OR = OR
    LEFT = relations_sql.FIELD
    VALUE = relations_sql.VALUE
    CONTAINS = relations_sql.CONTAINS

    def __init__(self, left=None, right=None, jsonify=False, **kwargs):

        if kwargs:
            left, right = list(kwargs.items())[0]

        if not isinstance(left, relations_sql.SQL):
            left = self.LEFT(left, jsonify=jsonify)

        if not isinstance(right, list):
            raise relations_sql.SQLError(self, f"right {right} must be list")

        self.expression = self.OR([self.CONTAINS(left, self.VALUE([value])) for value in right])


class NOTANY(ANY):
    """
    For if the left doesn't have any the members of right
    """

    NOT = relations_sql.NOT
    ANY = ANY

    def __init__(self, left=None, right=None, jsonify=False, **kwargs):

        self.expression = self.NOT(self.ANY(left, right, jsonify=jsonify, **kwargs))


class ALL(SETS):
    """
    For if the left and right have the same members
    """

    AND = AND
    CONTAINS = relations_sql.CONTAINS
    LENGTHS = relations_sql.LENGTHS

    def __init__(self, left=None, right=None, jsonify=False, **kwargs):

        self.expression = self.AND(self.CONTAINS(left, right, jsonify, **kwargs), self.LENGTHS(left, right, jsonify, **kwargs))


class NOTALL(ALL):
    """
    For if the left and right don't have the same members
    """

    NOT = relations_sql.NOT
    ALL = ALL

    def __init__(self, left=None, right=None, jsonify=False, **kwargs):

        self.expression = self.NOT(self.ALL(left, right, jsonify=jsonify, **kwargs))


class OP:
    """
    Determines the criterion based on operand
    """

    CRITERIONS = {
        'null': relations_sql.NULL,
        'eq': relations_sql.EQ,
        'ne': relations_sql.NE,
        'gt': relations_sql.GT,
        'gte': relations_sql.GTE,
        'lt': relations_sql.LT,
        'lte': relations_sql.LTE,
        'like': relations_sql.LIKE,
        'notlike': relations_sql.NOTLIKE,
        'in': relations_sql.IN,
        'notin': relations_sql.NOTIN,
        'has': HAS,
        'nothas': NOTHAS,
        'any': ANY,
        'notany': NOTANY,
        'all': ALL,
        'notall': NOTALL
    }

    def __new__(cls, *args, **kwargs):

        field = None
        value = None
        jsonify = kwargs.pop("JSONIFY", False)
        extracted = kwargs.pop("EXTRACTED", False)

        if len(args) == 2:
            field, value = args
        elif len(kwargs) == 1:
            field, value = list(kwargs.items())[0]
        else:
            raise relations_sql.SQLError(cls, f"need single pair in {kwargs} or double in {args}")

        operand = "eq"

        if '__' in field:
            pieces = field.rsplit('__', 1)
            if pieces[-1] in cls.CRITERIONS:
                field, operand = pieces

        return cls.CRITERIONS[operand](field, value, jsonify=jsonify, extracted=extracted)
