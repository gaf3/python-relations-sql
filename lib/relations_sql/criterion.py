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

    OPERAND = None # OPERAND to use as format string (if any)
    INVERT = None # OPERAND to use as format string (if not)
    PARENTHESES = False

    left = None    # Left expression
    right = None   # Right expression

    def __init__(self, left=None, right=None, invert=False, jsonify=False, extracted=False, **kwargs):

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
        self.express(self.right, sql, parentheses=isinstance(self.right, relations_sql.SELECT) or self.PARENTHESES)

        self.sql = self.INVERT % tuple(sql) if self.invert else self.OPERAND % tuple(sql)


class NULL(CRITERION):
    """
    For IS NULL and IS NOT NULL
    """

    OPERAND = "%s IS NULL"
    INVERT = "%s IS NOT NULL"

    def __len__(self):

        return 1

    def generate(self):

        sql = []
        self.args = []

        self.express(self.left, sql)

        OPERAND = self.INVERT if bool(self.right.value) == bool(self.invert) else self.OPERAND

        self.sql = OPERAND % tuple(sql)


class EQ(CRITERION):
    """
    For =
    """

    OPERAND = "%s=%s"
    INVERT = "%s!=%s"


class GT(CRITERION):
    """
    For >
    """

    OPERAND = "%s>%s"


class GTE(CRITERION):
    """
    For >=
    """

    OPERAND = "%s>=%s"


class LT(CRITERION):
    """
    For <
    """

    OPERAND = "%s<%s"


class LTE(CRITERION):
    """
    For <=
    """

    OPERAND = "%s<=%s"


class LIKE(CRITERION):
    """
    For fuzzy matching
    """

    OPERAND = "%s LIKE %s"
    INVERT = "%s NOT LIKE %s"

    BEFORE = "%"
    AFTER = "%"

    def __init__(self, left=None, right=None, invert=False, jsonify=False, extracted=False, **kwargs):

        if kwargs:
            left, right = list(kwargs.items())[0]

        if right is not None:
            right = f"{self.BEFORE}{right}{self.AFTER}"

        super().__init__(left, right, invert=invert, jsonify=jsonify, extracted=extracted)


class START(LIKE):
    """
    For fuzzy matching end of string
    """

    BEFORE = ""


class END(LIKE):
    """
    For fuzzy matching end of string
    """

    AFTER = ""


class IN(CRITERION):
    """
    For IN
    """

    RIGHT = relations_sql.LIST
    VALUE = relations_sql.VALUE

    OPERAND = "%s IN %s"
    INVERT = "%s NOT IN %s"
    PARENTHESES = True

    def generate(self):
        """
        Generate the left and right with operand in between
        """

        if self.right:

            super().generate()

        else:

            value = self.VALUE(self.invert)
            value.generate()
            self.sql = value.sql
            self.args = value.args

class CONTAINS(CRITERION):
    """
    Wether one set contains another
    """

    LEFT = relations_sql.FIELD
    RIGHT = relations_sql.VALUE

    OPERAND = "CONTAINS(%s,%s)"


class LENGTHS(CRITERION):
    """
    Wether one set contains another
    """

    LEFT = relations_sql.FIELD
    RIGHT = relations_sql.VALUE

    OPERAND = "LENGTHS(%s,%s)"
