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

    def create(self, *args, **kwargs):
        """
        Create on the Model
        """

        self.model.create(query=self, *args, **kwargs)

    def count(self, *args, **kwargs):
        """
        Create on the Model
        """

        self.model.count(query=self, *args, **kwargs)

    def titles(self, *args, **kwargs):
        """
        Create on the Model
        """

        self.model.titles(query=self, *args, **kwargs)

    def retrieve(self, *args, **kwargs):
        """
        Create on the Model
        """

        self.model.retrieve(query=self, *args, **kwargs)

    def update(self, *args, **kwargs):
        """
        Create on the Model
        """

        self.model.update(query=self, *args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Create on the Model
        """

        self.model.delete(query=self, *args, **kwargs)

    def generate(self, indent=0, count=0, pad=" ", **kwargs):
        """
        Generate the sql and args
        """

        sql = []
        self.args = []

        current = pad * (count * indent)
        line = "\n" if indent else ' '
        delimitter = f"{line}{current}"

        self.express(self.clauses.values(), sql, indent=indent, count=count, pad=" ", **kwargs)
        self.sql = f"{self.NAME}{line}{current}{delimitter.join(sql)}"


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

    def __init__(self, *args, **kwargs):

        super().__init__(**{key: value for key, value in kwargs.items() if key in self.CLAUSES})
        self.FIELDS(*args, **{key: value for key, value in kwargs.items() if key not in self.CLAUSES})

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
        ("TABLE", relations_sql.TABLE_NAME),
        ("COLUMNS", relations_sql.COLUMN_NAMES),
        ("VALUES", relations_sql.VALUES),
        ("SELECT", SELECT)
    ])

    def __init__(self, TABLE, *args, **kwargs): # pylint: disable=too-many-branches

        if args:
            kwargs["COLUMNS"] = [arg for arg in args if not isinstance(arg, dict)]
            args = [arg for arg in args if isinstance(arg, dict)]

        if args:
            kwargs["VALUES"] = args

        self.check(kwargs)

        for clause in self.CLAUSES:
            if clause == "TABLE":
                if isinstance(TABLE, self.CLAUSES["TABLE"]):
                    self.clauses[clause] = TABLE
                    self.clauses[clause].prefix = self.PREFIX
                else:
                    self.clauses[clause] = self.CLAUSES[clause](TABLE, prefix=self.PREFIX)
            elif clause == "COLUMNS":
                if "COLUMNS" in kwargs:
                    if isinstance(kwargs["COLUMNS"], self.CLAUSES["COLUMNS"]):
                        self.clauses[clause] = kwargs["COLUMNS"]
                    else:
                        self.clauses[clause] = self.CLAUSES[clause](kwargs["COLUMNS"])
                else:
                    self.clauses[clause] = self.CLAUSES[clause]([])
            elif clause == "VALUES":
                if "VALUES" in kwargs:
                    if isinstance(kwargs["VALUES"], self.CLAUSES["VALUES"]):
                        self.clauses[clause] = kwargs["VALUES"].bind(self)
                        self.column(self.clauses[clause].columns)
                    else:
                        self.clauses[clause] = self.CLAUSES[clause]().bind(self)
                        for values in kwargs["VALUES"]:
                            self.clauses[clause](values)
                else:
                    self.clauses[clause] = self.CLAUSES[clause]().bind(self)
            else:
                if clause in kwargs:
                    if isinstance(kwargs[clause], self.CLAUSES[clause]):
                        self.clauses[clause] = kwargs[clause].bind(self)
                    else:
                        self.clauses[clause] = self.CLAUSES[clause](kwargs[clause]).bind(self)
                else:
                    self.clauses[clause] = self.CLAUSES[clause]().bind(self)

    def column(self, columns):
        """
        Field the columns
        """

        if self.COLUMNS:
            return

        self.COLUMNS = self.CLAUSES["COLUMNS"](columns)

    def generate(self, indent=0, count=0, pad=" ", **kwargs):
        """
        Generate the sql and args
        """

        if self.VALUES and self.SELECT:
            raise relations_sql.SQLError(self, "set VALUES or SELECT but not both")

        super().generate(indent=indent, count=count, pad=pad, **kwargs)


class LIMITED(QUERY):
    """
    Clause that has a limit
    """

    def __init__(self, TABLE, **kwargs):

        self.check(kwargs)

        for clause in self.CLAUSES:
            if clause == "TABLE":
                if isinstance(TABLE, self.CLAUSES["TABLE"]):
                    self.clauses[clause] = TABLE
                    if self.PREFIX:
                        TABLE.prefix = self.PREFIX
                else:
                    self.clauses[clause] = self.CLAUSES[clause](TABLE, prefix=self.PREFIX)
            else:
                if clause in kwargs:
                    if isinstance(kwargs[clause], self.CLAUSES[clause]):
                        self.clauses[clause] = kwargs[clause].bind(self)
                    else:
                        self.clauses[clause] = self.CLAUSES[clause](kwargs[clause]).bind(self)
                else:
                    self.clauses[clause] = self.CLAUSES[clause]().bind(self)

    def generate(self, indent=0, count=0, pad=" ", **kwargs):
        """
        Generate the sql and args
        """

        if len(self.LIMIT) > 1:
            raise relations_sql.SQLError(self, "LIMIT can only be total")

        super().generate(indent=indent, count=count, pad=pad, **kwargs)


class UPDATE(LIMITED):
    """
    UPDATE query
    """

    NAME = "UPDATE"
    PREFIX = ""

    CLAUSES = collections.OrderedDict([
        ("OPTIONS", relations_sql.OPTIONS),
        ("TABLE", relations_sql.TABLE_NAME),
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
        ("TABLE", relations_sql.TABLE_NAME),
        ("WHERE", relations_sql.WHERE),
        ("ORDER_BY", relations_sql.ORDER_BY),
        ("LIMIT", relations_sql.LIMIT)
    ])
