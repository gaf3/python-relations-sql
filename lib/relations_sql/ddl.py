"""
Module for all Relations SQL Definition.
"""

import relations_sql


class DDL(relations_sql.EXPRESSION):
    """
    Base definiton
    """

    migration = None
    definition = None
    added = None

    def __init__(self, migration=None, definition=None, added=False, **kwargs):

        self.migration = migration
        self.definition = definition
        self.added = added

        if kwargs:
            self.migration = kwargs

        if self.migration and "store" not in self.migration and "name" in self.migration:
            self.migration["store"] = self.migration["name"]

        if self.definition and "store" not in self.definition:
            self.definition["store"] = self.definition["name"]

    def __len__(self):

        return 1

    def str(self, value):
        """
        Outputs string value for DDL
        """

        return f"{self.STR}{value}{self.STR}"

    def generate(self, **kwargs):

        self.args = []

        if self.migration is not None:
            if self.definition is None:
                if self.added:
                    self.add(**kwargs)
                else:
                    self.create(**kwargs)
            else:
                self.modify(**kwargs)
        else:
            self.drop(**kwargs)
