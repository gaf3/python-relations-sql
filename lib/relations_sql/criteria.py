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

    def generate(self, indent=0, count=0, pad=" ", **kwargs):
        """
        Concats the values
        """

        current = pad * (count * indent)
        next = current + (indent * pad)

        line = "\n" if indent else ''
        delimitter = f"{self.DELIMITTER.rstrip()}{line}{next}" if indent else self.DELIMITTER
        left, right = (f"({line}{next}", f"{line}{current})") if self.PARENTHESES else ('', '')

        sql = []
        self.sql = ""
        self.args = []

        if self:
            self.express(self.expressions, sql, indent=indent, count=count+1, pad=' ', **kwargs)
            self.sql = f"{left}{delimitter.join(sql)}{right}"


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


class SETS(relations_sql.CRITERION):
    """
    For comparing sets with each other
    """

    expression = None

    def __len__(self):

        return 1

    def generate(self, **kwargs):
        """
        Concats the values
        """

        self.expression.generate(**kwargs)
        self.sql = self.expression.sql
        self.args = self.expression.args

    @staticmethod
    def ensure(value):
        """
        Ensures the value is a list
        """

        if not isinstance(value, relations_sql.SQL) and not isinstance(value, (set, list)) and value is not None:
            return [value]

        return value


class HAS(SETS):
    """
    For if the left has all the members of right
    """

    CONTAINS = relations_sql.CONTAINS

    def __init__(self, left=None, right=None, invert=False, jsonify=False, extracted=False, **kwargs):

        if kwargs:
            left, right = list(kwargs.items())[0]

        right = self.ensure(right)

        self.expression = self.CONTAINS(left, right, invert=invert, jsonify=jsonify, extracted=extracted)


class ANY(SETS):
    """
    For if the left has any the members of right
    """

    OR = OR
    LEFT = relations_sql.COLUMN_NAME
    VALUE = relations_sql.VALUE
    CONTAINS = relations_sql.CONTAINS

    def __init__(self, left=None, right=None, invert=False, jsonify=False, extracted=False, **kwargs):

        if kwargs:
            left, right = list(kwargs.items())[0]

        if not isinstance(left, relations_sql.SQL):
            left = self.LEFT(left, jsonify=jsonify, extracted=extracted)

        right = self.ensure(right)

        self.expression = self.OR([self.CONTAINS(left, self.VALUE([value])) for value in right])


class ALL(SETS):
    """
    For if the left and right have the same members
    """

    AND = AND
    CONTAINS = relations_sql.CONTAINS
    LENGTHS = relations_sql.LENGTHS

    def __init__(self, left=None, right=None, invert=False, jsonify=False, extracted=False, **kwargs):

        right = self.ensure(right)

        self.expression = self.AND(
            self.CONTAINS(left, right, invert=invert, jsonify=jsonify, extracted=extracted, **kwargs),
            self.LENGTHS(left, right, invert=invert, jsonify=jsonify, extracted=extracted, **kwargs)
        )


class OP:
    """
    Determines the criterion based on operand
    """

    NOT = relations_sql.NOT

    CRITERIONS = {
        'null': relations_sql.NULL,
        'eq': relations_sql.EQ,
        'gt': relations_sql.GT,
        'gte': relations_sql.GTE,
        'lt': relations_sql.LT,
        'lte': relations_sql.LTE,
        'like': relations_sql.LIKE,
        'start': relations_sql.START,
        'end': relations_sql.END,
        'in': relations_sql.IN,
        'has': HAS,
        'any': ANY,
        'all': ALL
    }

    def __new__(cls, *args, **kwargs):

        field = None
        value = None
        invert = kwargs.pop("INVERT", False)
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
            elif pieces[-1].startswith('not_'):
                operands = pieces[-1].split('not_', 1)
                if operands[-1] in cls.CRITERIONS:
                    invert = True
                    field = pieces[0]
                    operand = operands[-1]

        if invert and cls.CRITERIONS[operand].INVERT is None:
            return cls.NOT(cls.CRITERIONS[operand](field, value, jsonify=jsonify, extracted=extracted))

        return cls.CRITERIONS[operand](field, value, invert=invert, jsonify=jsonify, extracted=extracted)
