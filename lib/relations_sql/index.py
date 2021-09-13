"""–
Module for Column DDL
"""

# pylint: disable=unused-argument

import relations_sql


class INDEX(relations_sql.DDL):
    """
    INDEX DDL
    """

    TABLE = None
    COLUMNS = None

    CREATE = "INDEX"
    MODIFY = None

    def __init__(self, migration=None, definition=None, added=False, **kwargs):

        super().__init__(migration=migration, definition=definition, added=added, **kwargs)

        if self.migration is None:
            return

        if "table" in self.migration and isinstance(self.migration["table"], str):
            self.migration["table"] = {"name": self.migration["table"]}

        if "schema" in self.migration:
            self.migration["table"]["schema"] = self.migration.pop("schema")

    def name(self, definition=False, full=True):
        """
        Generate a quoted name, with store as the default
        """

        state = self.definition if definition else self.migration
        name = state['store'] if 'store' in state else state['name']

        table = self.TABLE(**state["table"]) if state.get("table") else None

        if table:
            name = f"{table.name}_{name}"

        name = name.replace("-", "_")

        sql = []

        if table and full and table.schema:
            sql.append(self.quote(table.schema.name))

        sql.append(self.quote(name))

        return self.SEPARATOR.join(sql)

    def create(self, **kwargs):
        """
        CREATE DLL
        """

        sql = []

        if "table" in self.migration:
            sql.append("CREATE")

        sql.append(self.CREATE)
        sql.append(self.name(full=False))

        if self.migration.get("table"):
            table = self.TABLE(**self.migration['table'])
            table.generate()
            sql.append(f"ON {table.sql}")

        columns = self.COLUMNS(self.migration["columns"])
        columns.generate()
        sql.append(columns.sql)

        self.sql = " ".join(sql)

    def add(self, **kwargs):
        """
        ADD DLL
        """

        self.create()

        if "table" not in self.migration:
            self.sql = f"ADD {self.sql}"

    def modify(self, **kwargs):
        """
        MODIFY DLL
        """

        self.sql = self.MODIFY % (self.name(definition=True), self.name())

    def drop(self, **kwargs):
        """
        DROP DLL
        """

        self.sql = f"DROP INDEX {self.name(definition=True)}"


class UNIQUE(INDEX):
    """
    UNIQUE INDEX DDL
    """

    TABLE = None
    COLUMNS = None

    CREATE = "UNIQUE"
