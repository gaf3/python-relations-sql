"""
Module for all Relations SQL Expressions. pieces of criterions, criteria, and statements
"""

import json
import collections.abc

import relations_sql


class EXPRESSION(relations_sql.SQL):
    """
    Base class for expressions
    """

    def __len__(self):

        return 1

    def quote(self, value):
        """
        Quote name if we hae quotes
        """

        if self.QUOTE is not None:
            return f"{self.QUOTE}{value}{self.QUOTE}"

        return value

    def express(self, expression, sql, **kwargs):
        """
        Add this expression's generation to our own
        """

        if isinstance(expression, collections.abc.Iterable):
            for each in expression:
                self.express(each, sql, **kwargs)
        elif expression:
            expression.generate(**kwargs)
            sql.append(expression.sql)
            self.args.extend(expression.args)


class VALUE(EXPRESSION):
    """
    Class for storing a value that will need to be escaped
    """

    value = None # the value
    jsonify = None # whether this value will be used with JSON

    def __init__(self, value, jsonify=False):

        self.value = value
        self.jsonify = jsonify or (value is not None and not isinstance(value, (bool, int, float, str)))

    def generate(self, **kwargs):

        if self.jsonify:
            self.sql = self.JSONIFY % self.PLACEHOLDER
            self.args = [json.dumps(sorted(list(self.value)) if isinstance(self.value, set) else self.value)]
        else:
            self.sql = self.PLACEHOLDER
            self.args = [self.value]


class NOT(EXPRESSION):
    """
    Negation
    """

    VALUE = VALUE

    expression = None

    def __init__(self, expression):

        self.expression = expression if isinstance(expression, relations_sql.SQL) else self.VALUE(expression)

    def generate(self, indent=0, count=0, pad=' ', **kwargs):

        self.args = []

        self.express(self.expression, [], indent=indent, count=count+1, pad=pad, **kwargs)
        self.sql = f"NOT {self.expression.sql}"


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

    def generate(self, indent=0, count=0, pad=' ', **kwargs):

        sql = []
        self.args = []

        current = pad * (count * indent)
        line = "\n" if indent else ''

        for expression in self.expressions:
            self.express(expression, sql, indent=indent, count=count+1, pad=pad, **kwargs)

        self.sql = f",{line}{current}".join(sql)


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

    def generate(self, **kwargs):

        self.sql = self.quote(self.name)
        self.args = []


class SCHEMA_NAME(NAME):
    """
    For schemas
    """


class TABLE_NAME(SCHEMA_NAME):
    """
    For tables
    """

    SCHEMA_NAME = SCHEMA_NAME

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
            self.schema = schema if isinstance(schema, relations_sql.SQL) else self.SCHEMA_NAME(schema)
        elif len(pieces) == 1:
            self.schema = self.SCHEMA_NAME(pieces[0])

        self.prefix = prefix

    def generate(self, indent=0, count=0, pad=' ', **kwargs):

        sql = []
        self.args = []

        if self.schema:
            self.express(self.schema, sql, **kwargs)

        sql.append(self.quote(self.name))

        self.sql = self.SEPARATOR.join(sql)

        one = pad * indent
        current = pad * (count * indent)
        next = current + (indent * pad)
        line = "\n" if indent else ' '

        if self.prefix is not None:
            self.sql = f"{self.prefix}{line}{next}{self.sql}" if self.prefix else f"{one}{self.sql}"


class COLUMN_NAME(TABLE_NAME):
    """
    Class for storing a column that'll be used as a column
    """

    TABLE_NAME = TABLE_NAME

    table = None  # name of the table

    jsonify = None # whether we need to cast this column as JSON
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
            self.table = table if isinstance(table, relations_sql.SQL) else self.TABLE_NAME(table, schema)

        self.jsonify = jsonify

    def column(self, **kwargs):
        """
        Generates the column with table and schema
        """

        sql = []

        if self.table:
            self.express(self.table, sql, **kwargs)

        sql.append('*' if self.name == '*' else self.quote(self.name))

        return self.SEPARATOR.join(sql)

    def generate(self, **kwargs):
        """
        Generates the sql and args
        """

        self.args = []

        column = self.column(**kwargs)

        if self.path:
            self.sql = self.PATH % (column, self.PLACEHOLDER)
            self.args.append(self.walk(self.path))
        else:
            self.sql = column

        if self.jsonify:
            self.sql = self.JSONIFY % self.sql


class NAMES(LIST):
    """
    Holds a list of column names only, with table
    """

    ARG = NAME

    def __init__(self, expressions):

        self.expressions = []

        for expression in expressions:
            if isinstance(expression, relations_sql.SQL):
                self.expressions.append(expression)
            else:
                self.expressions.append(self.ARG(expression))


class COLUMN_NAMES(NAMES):
    """
    Holds a list of column names only, with table
    """

    ARG = COLUMN_NAME

    def __init__(self, expressions):

        self.expressions = []

        for expression in expressions:
            if isinstance(expression, relations_sql.SQL):
                self.expressions.append(expression)
            else:
                self.expressions.append(self.ARG(expression, extracted=True))

    def generate(self, indent=0, count=0, pad=' ', **kwargs):
        """
        Generates the sql and args
        """

        count += 1
        current = pad * (count * indent)
        next = current + (indent * pad)

        one = pad * indent
        line = "\n" if indent else ''
        delimitter = f",{line}{next}"
        left, right = (f"{one}({line}{next}", f"{line}{current})")

        sql = []
        self.args = []

        self.express(self.expressions, sql, indent=indent, count=count+1, pad=' ', **kwargs)
        self.sql = f"{left}{delimitter.join(sql)}{right}"


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

    def generate(self, indent=0, count=0, pad=' ', **kwargs):
        """
        Generates the sql and args
        """

        sql = []
        self.args = []

        current = pad * (count * indent)
        next = current + (indent * pad)
        line = "\n" if indent else ''
        left, right = (f"({line}{next}", f"{line}{current})") if isinstance(self.expression, relations_sql.SELECT) else ('', '')

        self.express(self.expression, sql, indent=indent, count=count+1, **kwargs)
        self.express(self.label, sql, indent=indent, count=count+1, **kwargs)

        self.sql = f"{left}{sql[0]}{right} AS {sql[1]}"


ASC = -1
DESC = 1

class ORDER(EXPRESSION):
    """
    For anything that needs to be ordered
    """

    EXPRESSION = COLUMN_NAME

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

    def generate(self, **kwargs):

        sql = []
        self.args = []

        if self.expression:
            self.express(self.expression, sql, **kwargs)
            if self.ORDER.get(self.order) is not None:
                sql.append(self.ORDER[self.order])

        self.sql = " ".join(sql)


class ASSIGN(EXPRESSION):
    """
    For SET pairings
    """

    COLUMN_NAME = COLUMN_NAME
    EXPRESSION = VALUE

    column = None
    expression = None

    def __init__(self, column, expression):

        self.column = column if isinstance(column, relations_sql.SQL) else self.COLUMN_NAME(column)
        self.expression = expression if isinstance(expression, relations_sql.SQL) else self.EXPRESSION(expression)

    def __len__(self):

        return len(self.column) + len(self.expression)

    def generate(self, indent=0, count=0, pad=' ', **kwargs):
        """
        Generates the sql and args
        """

        sql = []
        self.args = []

        current = pad * (count * indent)
        next = current + (indent * pad)
        line = "\n" if indent else ''
        left, right = (f"({line}{next}", f"{line}{current})") if isinstance(self.expression, relations_sql.SELECT) else ('', '')

        self.express(self.column, sql, indent=indent, count=count+1, **kwargs)
        self.express(self.expression, sql, indent=indent, count=count+1, **kwargs)

        self.sql = f"{sql[0]}={left}{sql[1]}{right}"
