"""
Module for all Relations SQL Queries.
"""

import collections

import relations_sql

class QUERY(relations_sql.EXPRESSION):
    """
    Base query
    """

    NAME = None
    PREFIX = None

    CLAUSES = None
    clauses = None

    MODEL = [
        'create',
        'count',
        'retrieve',
        'labels',
        'update',
        'delete'
    ]
    model = None

    def __init__(self, **kwargs):

        self.check(kwargs)

        for clause in self.CLAUSES:
            if clause in kwargs:
                if isinstance(kwargs[clause], self.CLAUSES[clause]):
                    self.clauses[clause] = kwargs[clause].bind(self)
                else:
                    self.clauses[clause] = self.CLAUSES[clause](kwargs[clause]).bind(self)
            else:
                self.clauses[clause] = self.CLAUSES[clause]().bind(self)

    def __getattr__(self, name):
        """
        Used to get clauses directly
        """

        if name in self.CLAUSES:
            return self.clauses[name]

        if name in self.MODEL and self.model is not None:
            return getattr(self.model, name)

        raise AttributeError(f"'{self}' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        """
        Used to gset clauses directly
        """

        if name in self.CLAUSES:
            self.clauses[name] = value
        else:
            object.__setattr__(self, name, value)

    def __len__(self):

        return sum(len(clause) for clause in self.clauses.values())

    def check(self, kwargs):
        """
        Check kwargs to make sure there's nothing extra
        """

        for clause in kwargs:
            if clause not in self.CLAUSES:
                raise TypeError(f"'{clause}' is an invalid keyword argument for {self.__class__.__name__}")

        self.clauses = collections.OrderedDict()

    def bind(self, model):
        """
        Binds the model
        """

        self.model = model
        return self

    def generate(self):
        """
        Generate the sql and args
        """

        sql = []
        self.args = []

        self.express(self.clauses.values(), sql)
        self.sql = f"{self.NAME} {' '.join(sql)}"


class SELECT(QUERY):
    """
    SELECT
    """

    NAME = "SELECT"

    CLAUSES = collections.OrderedDict([
        ("OPTIONS", relations_sql.OPTIONS),
        ("FIELDS", relations_sql.FIELDS),
        ("FROM", relations_sql.FROM),
        ("WHERE", relations_sql.WHERE),
        ("GROUP_BY", relations_sql.GROUP_BY),
        ("HAVING", relations_sql.HAVING),
        ("ORDER_BY", relations_sql.ORDER_BY),
        ("LIMIT", relations_sql.LIMIT)
    ])

    parentheses = False

    def __init__(self, *args, **kwargs):

        super().__init__(*kwargs)
        self.FIELDS(*args)

    def __call__(self, *args, **kwargs):
        """
        Shorthand for FIELDS
        """
        return self.FIELDS(*args, **kwargs)


class INSERT(QUERY):
    """
    INSERT query
    """

    NAME = "INSERT"
    PREFIX = "INTO"

    CLAUSES = collections.OrderedDict([
        ("OPTIONS", relations_sql.OPTIONS),
        ("TABLE", relations_sql.TABLE),
        ("FIELDS", relations_sql.NAMES),
        ("VALUES", relations_sql.VALUES),
        ("SELECT", SELECT)
    ])

    def __init__(self, table, *args, **kwargs):

        self.check(kwargs)

        for clause in self.CLAUSES:
            if clause == "TABLE":
                self.clauses[clause] = self.CLAUSES[clause](table, prefix=self.PREFIX)
            elif clause == "FIELDS":
                if "FIELDS" in kwargs:
                    self.clauses[clause] = self.CLAUSES[clause](kwargs["FIELDS"])
                else:
                    self.clauses[clause] = self.CLAUSES[clause](args)
            else:
                if clause in kwargs:
                    if isinstance(kwargs[clause], self.CLAUSES[clause]):
                        self.clauses[clause] = kwargs[clause].bind(self)
                    else:
                        self.clauses[clause] = self.CLAUSES[clause](kwargs[clause]).bind(self)
                else:
                    self.clauses[clause] = self.CLAUSES[clause]().bind(self)

    def field(self, fields):
        """
        Field the fields
        """

        if self.FIELDS:
            return

        self.FIELDS = self.CLAUSES["FIELDS"](fields)

    def generate(self):
        """
        Generate the sql and args
        """

        if self.VALUES and self.SELECT:
            raise relations_sql.SQLError(self, "set VALUES or SELECT but not both")

        sql = []
        self.args = []

        for clause in self.CLAUSES:
            self.express(self.clauses[clause], sql, parentheses=(clause == "FIELDS"))

        self.sql = f"{self.NAME} {' '.join(sql)}"


class LIMITED(QUERY):
    """
    Clause that has a limit
    """

    def __init__(self, table, **kwargs):

        self.check(kwargs)

        for clause in self.CLAUSES:
            if clause == "TABLE":
                self.clauses[clause] = self.CLAUSES[clause](table, prefix=self.PREFIX)
            else:
                if clause in kwargs:
                    if isinstance(kwargs[clause], self.CLAUSES[clause]):
                        self.clauses[clause] = kwargs[clause].bind(self)
                    else:
                        self.clauses[clause] = self.CLAUSES[clause](kwargs[clause]).bind(self)
                else:
                    self.clauses[clause] = self.CLAUSES[clause]().bind(self)

    def generate(self):
        """
        Generate the sql and args
        """

        if len(self.LIMIT) > 1:
            raise relations_sql.SQLError(self, "LIMIT can only be total")

        super().generate()


class UPDATE(LIMITED):
    """
    UPDATE query
    """

    NAME = "UPDATE"

    CLAUSES = collections.OrderedDict([
        ("OPTIONS", relations_sql.OPTIONS),
        ("TABLE", relations_sql.TABLE),
        ("SET", relations_sql.SET),
        ("WHERE", relations_sql.WHERE),
        ("ORDER_BY", relations_sql.ORDER_BY),
        ("LIMIT", relations_sql.LIMIT)
    ])


class DELETE(LIMITED):
    """
    DELETE query
    """

    NAME = "DELETE"
    PREFIX = "FROM"

    CLAUSES = collections.OrderedDict([
        ("OPTIONS", relations_sql.OPTIONS),
        ("TABLE", relations_sql.TABLE),
        ("WHERE", relations_sql.WHERE),
        ("ORDER_BY", relations_sql.ORDER_BY),
        ("LIMIT", relations_sql.LIMIT)
    ])