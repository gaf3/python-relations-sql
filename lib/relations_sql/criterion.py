"""
Module for all Relations SQL Criterions, pieces of Criteria
"""

import relations_sql

class CRITERION(relations_sql.EXPRESSION):
    """
    CRITERION class, for comparing two values
    """

    LEFT = None
    RIGHT = None

    OPERAND = None # OPERAND to use (if any)
    INVERT = None # OPERAND to use (if not)

    left = None    # Left expression
    right = None   # Right expression
    invert = False  # Whether to invert the relationship

    def __init__(self, left=None, right=None, invert=invert, jsonify=False, extracted=False, **kwargs):

        if invert and self.INVERT is None:
            raise relations_sql.SQLError(self, "no invert without INVERT operand")

        if kwargs:
            left, right = list(kwargs.items())[0]

        if not isinstance(left, relations_sql.SQL):
            left = self.LEFT(left, jsonify=jsonify, extracted=extracted)

        if isinstance(left, relations_sql.FIELD) and left.path:
            jsonify = True

        if not isinstance(right, relations_sql.SQL):
            right = self.RIGHT(right, jsonify=jsonify)

        self.left = left
        self.right = right
        self.invert = invert

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

        self.sql = self.INVERT.join(sql) if self.invert else self.OPERAND.join(sql)


class NULL(CRITERION):
    """
    For IS NULL and IS NOT NULL
    """

    OPERAND = "IS NULL"
    INVERT = "IS NOT NULL"

    def __len__(self):

        return 1

    def generate(self):

        sql = []
        self.args = []

        self.express(self.left, sql)

        OPERAND = self.INVERT if bool(self.right.value) == bool(self.invert) else self.OPERAND

        self.sql = f"%s %s" % (self.left.sql, OPERAND)


class EQ(CRITERION):
    """
    For =
    """

    OPERAND = "="
    INVERT = "!="


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
    INVERT = " NOT LIKE "


class IN(CRITERION):
    """
    For IN
    """

    RIGHT = relations_sql.LIST
    VALUE = relations_sql.VALUE

    OPERAND = " IN "
    INVERT = " NOT IN "

    def generate(self):
        """
        Generate the left and right with operand in between
        """

        if self.right:

            sql = []
            self.args = []

            self.express(self.left, sql)
            self.express(self.right, sql, parentheses=True)

            self.sql = self.INVERT.join(sql) if self.invert else self.OPERAND.join(sql)

        else:

            value = self.VALUE(self.invert)
            value.generate()
            self.sql = value.sql
            self.args = value.args


class RANGES(CRITERION):
    """
    RANGES class, for criterions of sets
    """

    def generate(self):
        """
        Generate the left and right with operand in between
        """

        sql = []
        self.args = []

        self.express(self.left, sql)
        self.express(self.right, sql, parentheses=isinstance(self.right, relations_sql.SELECT))

        self.sql = self.OPERAND % (self.left.sql, self.right.sql)


class CONTAINS(RANGES):
    """
    Wether one set contains another
    """

    LEFT = relations_sql.FIELD
    RIGHT = relations_sql.VALUE

    OPERAND = "CONTAINS(%s,%s)"


class LENGTHS(RANGES):
    """
    Wether one set contains another
    """

    LEFT = relations_sql.FIELD
    RIGHT = relations_sql.VALUE

    OPERAND = "LENGTHS(%s,%s)"
