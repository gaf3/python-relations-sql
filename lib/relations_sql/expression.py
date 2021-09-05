"""
Module for all Relations SQL Expressions. pieces of criterions, criteria, and statements
"""

import json
import collections.abc

import relations
import relations_sql


class EXPRESSION(relations_sql.SQL):
    """
    Base class for expressions
    """

    QUOTE = None

    def quote(self, value):
        """
        Quote name if we hae quotes
        """

        if self.QUOTE is not None:
            return f"{self.QUOTE}{value}{self.QUOTE}"

        return value

    def express(self, expression, sql, parentheses=False):
        """
        Add this expression's generation to our own
        """

        if isinstance(expression, collections.abc.Iterable):
            for each in expression:
                self.express(each, sql)
            return

        if expression:
            expression.generate()
            sql.append(f"({expression.sql})" if parentheses else expression.sql)
            self.args.extend(expression.args)


class VALUE(EXPRESSION):
    """
    Class for storing a value that will need to be escaped
    """

    PLACEHOLDER = None
    JSONIFY = None

    value = None # the value
    jsonify = None # whether this value will be used with JSON

    def __init__(self, value, jsonify=False):

        self.value = value
        self.jsonify = jsonify or not isinstance(value, (bool, int, float, str))

    def __len__(self):

        return 1

    def generate(self):

        if self.jsonify:
            self.sql = self.JSONIFY % self.PLACEHOLDER
            self.args = [json.dumps(self.value)]
        else:
            self.sql = self.PLACEHOLDER
            self.args = [self.value]


class NOT(EXPRESSION):
    """
    Negation
    """

    VALUE = VALUE

    OPERAND = "NOT %s"

    expression = None

    def __init__(self, expression):

        self.expression = expression if isinstance(expression, relations_sql.SQL) else self.VALUE(expression)

    def generate(self):

        self.args = []

        self.express(self.expression, [])
        self.sql = self.OPERAND % self.expression.sql


class LIST(EXPRESSION):
    """
    Holds a list of values for IN, NOT IN, and VALUES
    """

    ARG = VALUE

    expressions = None

    def __init__(self, expressions, jsonify=False):

        self.expressions = []
        self.jsonify = jsonify

        for expression in expressions:
            if isinstance(expression, relations_sql.SQL):
                self.expressions.append(expression)
            else:
                self.expressions.append(self.ARG(expression, jsonify=jsonify))

    def __len__(self):

        return len(self.expressions)

    def generate(self):

        sql = []
        self.args = []

        for expression in self.expressions:
            self.express(expression, sql)

        self.sql = ','.join(sql)


class NAME(EXPRESSION):
    """
    For anything that needs to be quote
    """

    name = None

    def __init__(self, name):

        self(name)

    def __len__(self):

        return 1 if self.name is not None else 0

    def __call__(self, name):

        self.set(name)

    def set(self, name):
        """
        Set the NAME explicitly
        """
        self.name = name

    def generate(self):

        self.sql = self.quote(self.name)
        self.args = []


class SCHEMA(NAME):
    """
    For schemas
    """


class TABLE(SCHEMA):
    """
    For tables
    """

    SCHEMA = SCHEMA

    SEPARATOR = None

    schema = None

    prefix = None

    def __init__(self, name, schema=None, prefix=None):

        self(name, schema, prefix)

    def __call__(self, name, schema=None, prefix=None):

        self.set(name, schema, prefix)

    def set(self, name, schema=None, prefix=None):

        pieces = name.split(self.SEPARATOR)

        self.name = pieces.pop(-1)

        if schema is not None:
            self.schema = schema if isinstance(schema, relations_sql.SQL) else self.SCHEMA(schema)
        elif len(pieces) == 1:
            self.schema = self.SCHEMA(pieces[0])

        self.prefix = prefix

    def generate(self):

        sql = []
        self.args = []

        if self.schema:
            self.express(self.schema, sql)

        sql.append(self.quote(self.name))

        self.sql = self.SEPARATOR.join(sql)

        if self.prefix:
            self.sql = f"{self.prefix} {self.sql}"


class FIELD(TABLE):
    """
    Class for storing a column that'll be used as a field
    """

    PLACEHOLDER = None
    JSONIFY = None
    PATH = None

    TABLE = TABLE

    table = None  # name of the table

    jsonify = None # whether we need to cast this field as JSON
    path = None     # path to use in the JSON

    def __init__(self, name, table=None, schema=None, jsonify=False, extracted=False):

        self(name, table, schema, jsonify, extracted)

    def __call__(self, name, table=None, schema=None, jsonify=False, extracted=False):

        self.set(name, table, schema, jsonify, extracted)

    def set(self, name, table=None, schema=None, jsonify=False, extracted=False):

        pieces = name.split(self.SEPARATOR)

        self.name, self.path = self.split(pieces.pop(-1)) if not extracted else (pieces.pop(-1), [])

        if pieces:
            piece = pieces.pop(-1)
            if table is None:
                table = piece

        if pieces:
            piece = pieces.pop(-1)
            if schema is None:
                schema = piece

        if table is not None:
            self.table = table if isinstance(table, relations_sql.SQL) else self.TABLE(table, schema)

        self.jsonify = jsonify

    @staticmethod
    def split(field):
        """
        Splits field value into name and path
        """

        path = relations.Field.split(field)

        name = path.pop(0)

        return name, path

    def field(self):
        """
        Generates the field with tbale and schema
        """

        sql = []

        if self.table:
            self.express(self.table, sql)

        sql.append('*' if self.name == '*' else self.quote(self.name))

        return self.SEPARATOR.join(sql)

    def generate(self):
        """
        Generates the sql and args
        """

        self.args = []

        field = self.JSONIFY % self.field() if self.jsonify else self.field()

        if self.path:
            self.sql = self.PATH % (field, self.PLACEHOLDER)
            self.args.append(self.walk())
        else:
            self.sql = field


class NAMES(LIST):
    """
    Holds a list of field names only, with table
    """

    ARG = NAME

    def __init__(self, expressions):

        self.expressions = []

        for expression in expressions:
            if isinstance(expression, relations_sql.SQL):
                self.expressions.append(expression)
            else:
                self.expressions.append(self.ARG(expression))


class AS(EXPRESSION):
    """
    For AS pairings
    """

    NAME = NAME

    label = None
    expression = None

    def __init__(self, label, expression):

        self.label = label if isinstance(label, relations_sql.SQL) else self.NAME(label)
        self.expression = expression

    def __len__(self):

        return len(self.label) + len(self.expression)

    def generate(self):
        """
        Generates the sql and args
        """

        sql = []
        self.args = []

        self.express(self.expression, sql, parentheses=isinstance(self.expression, relations_sql.SELECT))
        self.express(self.label, sql)

        self.sql = " AS ".join(sql)

ASC = -1
DESC = 1

class ORDER(EXPRESSION):
    """
    For anything that needs to be ordered
    """

    EXPRESSION = FIELD

    expression = None
    order = None

    ORDER = {
        ASC: "ASC",
        DESC: "DESC"
    }

    def __init__(self, expression=None, order=None, **kwargs):

        if kwargs:
            if len(kwargs) != 1:
                raise relations_sql.SQLError(self, f"need single pair in {kwargs}")
            expression, order = list(kwargs.items())[0]

        if order is not None and order not in self.ORDER:
            raise relations_sql.SQLError(self, f"order {order} must be in {list(self.ORDER.keys())}")

        self.expression = expression if isinstance(expression, relations_sql.SQL) else self.EXPRESSION(expression)
        self.order = order

    def __len__(self):

        return len(self.expression)

    def generate(self):

        sql = []
        self.args = []

        if self.expression:
            self.express(self.expression, sql)
            if self.ORDER.get(self.order) is not None:
                sql.append(self.ORDER[self.order])

        self.sql = " ".join(sql)


class ASSIGN(EXPRESSION):
    """
    For SET pairings
    """

    FIELD = NAME
    EXPRESSION = VALUE

    field = None
    expression = None

    def __init__(self, field, expression):

        self.field = field if isinstance(field, relations_sql.SQL) else self.FIELD(field)
        self.expression = expression if isinstance(expression, relations_sql.SQL) else self.EXPRESSION(expression)

    def __len__(self):

        return len(self.field) + len(self.expression)

    def generate(self):
        """
        Generates the sql and args
        """

        sql = []
        self.args = []

        self.express(self.field, sql)
        self.express(self.expression, sql)

        self.sql = "=".join(sql)
