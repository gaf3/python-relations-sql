"""
Module for all Relations SQL Criterions, pieces of Criteria
"""

import relations_sql

class CRITERION(relations_sql.EXPRESSION):
    """
    CRITERION class, for comparing two values
    """

    LEFT = relations_sql.FIELD
    RIGHT = relations_sql.VALUE

    OPERAND = None # OPERAND to use (if any)

    left = None    # Left expression
    right = None   # Right expression

    def __init__(self, left=None, right=None, jsonify=False, **kwargs):

        if kwargs:
            left, right = list(kwargs.items())[0]

        if not isinstance(left, relations_sql.SQL):
            left = self.LEFT(left, jsonify=jsonify)

        if isinstance(left, relations_sql.FIELD) and left.path:
            jsonify = True

        if not isinstance(right, relations_sql.SQL):
            right = self.RIGHT(right, jsonify=jsonify)

        self.left = left
        self.right = right

    def __len__(self):

        return len(self.left) + len(self.right)

    def generate(self):
        """
        Generate the left and right with operand in between
        """

        sql = []
        self.args = []

        self.express(self.left, sql)
        self.express(self.right, sql, parentheses=isinstance(self.right, relations_sql.SELECT))

        self.sql = self.OPERAND.join(sql)


class NULL(CRITERION):
    """
    For IS NULL and IS NOT NULL
    """

    OPERAND = "NULL"

    def __len__(self):

        return 1

    def generate(self):

        sql = []
        self.args = []

        self.express(self.left, sql)
        sql.append('IS' if self.right.value else 'IS NOT')
        sql.append(self.OPERAND)

        self.sql = ' '.join(sql)


class EQ(CRITERION):
    """
    For =
    """

    OPERAND = "="


class NE(CRITERION):
    """
    For =
    """

    OPERAND = "!="


class GT(CRITERION):
    """
    For >
    """

    OPERAND = ">"


class GTE(CRITERION):
    """
    For >=
    """

    OPERAND = ">="


class LT(CRITERION):
    """
    For <
    """

    OPERAND = "<"


class LTE(CRITERION):
    """
    For <=
    """

    OPERAND = "<="


class LIKE(CRITERION):
    """
    For fuzzy matching
    """

    OPERAND = " LIKE "


class NOTLIKE(CRITERION):
    """
    For fuzzy mismatching
    """

    OPERAND = " NOT LIKE "


class RANGE(CRITERION):
    """
    RANGE class, for comparing a value against a set of values
    """

    VALUE = None

    EMPTY = None

    def generate(self):
        """
        Generate the left and right with operand in between
        """

        if self.right:

            sql = []
            self.args = []

            self.express(self.left, sql)
            self.express(self.right, sql, parentheses=True)

            self.sql = self.OPERAND.join(sql)

        else:

            value = self.VALUE(self.EMPTY)
            value.generate()
            self.sql = value.sql
            self.args = value.args


class IN(RANGE):
    """
    For IN
    """

    RIGHT = relations_sql.LIST
    VALUE = relations_sql.VALUE

    EMPTY = False

    OPERAND = " IN "


class NOTIN(RANGE):
    """
    For NOT IN
    """

    RIGHT = relations_sql.LIST
    VALUE = relations_sql.VALUE

    EMPTY = True

    OPERAND = " NOT IN "


class RANGES(RANGE):
    """
    RANGES class, for comparing sets of values
    """


class HAS(RANGES):
    """
    For if the left has all the members of right
    """


class NOTHAS(RANGES):
    """
    For if the left doesn't have all the members of right
    """


class ANY(RANGES):
    """
    For if the left has any the members of right
    """


class NOTANY(RANGES):
    """
    For if the left doesn't have any the members of right
    """


class ALL(RANGES):
    """
    For if the left and right have the same members
    """


class NOTALL(RANGES):
    """
    For if the left and right don't have the same members
    """


class OP:
    """
    Determines the criterion based on operand
    """

    CRITERIONS = {
        'null': NULL,
        'eq': EQ,
        'ne': NE,
        'gt': GT,
        'gte': GTE,
        'lt': LT,
        'lte': LTE,
        'like': LIKE,
        'notlike': NOTLIKE,
        'in': IN,
        'notin': NOTIN,
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

        return cls.CRITERIONS[operand](field, value)
