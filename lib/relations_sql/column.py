"""
Module for Column DDL
"""

# pylint: disable=unused-argument

import json

import relations_sql

class COLUMN(relations_sql.DDL):
    """
    COLUMN DDL
    """

    KINDS = {}

    COLUMN_NAME = None

    STORE = None
    KIND = None
    EXTRACT = None
    SET_DEFAULT = None
    UNSET_DEFAULT = None
    SET_NONE = None
    UNSET_NONE = None

    def name(self, definition=False):
        """
        Generate a quoted name, with store as the default
        """

        state = self.definition if definition or "store" not in self.migration else self.migration

        return self.quote(state['store'])

    def create(self, **kwargs):
        """
        CREATE DLL
        """

        sql = [self.name()]

        sql.append(self.KINDS.get(self.migration['kind'], self.KINDS["json"]))

        if "__" in self.migration["store"]:

            name, path = self.COLUMN_NAME.split(self.migration["store"])
            sql.append(self.EXTRACT % (self.PATH % (self.quote(name), self.COLUMN_NAME.walk(path))))

        else:

            if not self.migration.get('none'):
                sql.append("NOT NULL")

            if self.migration.get('default') is not None:
                if isinstance(self.migration.get('default'), (bool, int, float, str)):
                    default = self.migration.get('default')
                else:
                    default = json.dumps(self.migration.get('default'))
                quote = self.STR if isinstance(default, str) else ''
                sql.append(f"DEFAULT {quote}{default}{quote}")

        self.sql = " ".join(sql)

    def add(self, **kwargs):
        """
        ADD DLL
        """

        self.create()

        self.sql = f"ADD {self.sql}"

    def store(self, sql):
        """
        Modifies the store
        """
        sql.append(self.STORE % (self.name(definition=True), self.name()))

    def kind(self, sql):
        """
        Modifies the kind
        """
        sql.append(self.KIND % (self.name(), self.KINDS.get(self.migration['kind'], self.KINDS["json"])))

    def default(self, sql):
        """
        Modifies the default
        """
        if self.migration.get("default") is not None:
            default = self.migration["default"]
            quote = self.STR if isinstance(default, str) else ''
            sql.append(self.SET_DEFAULT % (self.name(), f"{quote}{default}{quote}"))
        else:
            sql.append(self.UNSET_DEFAULT % self.name())

    def none(self, sql):
        """
        Modifies none
        """

        if self.migration["none"]:
            sql.append(self.UNSET_NONE % self.name())
        else:
            sql.append(self.SET_NONE % self.name())

    def modify(self, indent=0, count=0, pad=' ', **kwargs):
        """
        MODIFY DLL
        """

        sql = []

        if "store" in self.migration:
            self.store(sql)

        if "kind" in self.migration:
            self.kind(sql)

        if "default" in self.migration:
            self.default(sql)

        if "none" in self.migration:
            self.none(sql)

        current = pad * (count * indent)# pylint: disable=unused-argument
        delimitter = f",\n{current}" if indent else ','

        self.sql = delimitter.join(sql)

    def drop(self, **kwargs):
        """
        DROP DLL
        """

        self.sql = f"DROP {self.quote(self.definition['store'])}"
