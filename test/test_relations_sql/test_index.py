import unittest
import unittest.mock

import test_ddl
import test_expression

import relations
import relations_sql


class INDEX(test_ddl.DDL, relations_sql.INDEX):

    TABLE = test_expression.TABLENAME
    COLUMNS = test_expression.COLUMNNAMES

    MODIFY = "MODIFY %s TO %s"

class TestINDEX(unittest.TestCase):

    maxDiff = None

    def test___init__(self):

        INDEX()

        ddl = INDEX(migration={}, schema="people", table="stuff")

        self.assertEqual(ddl.migration, {"table": {"schema": "people", "name": "stuff"}})

    def test_name(self):

        ddl = INDEX(schema="people", table="stuff", name="things", definition={"name": "people-stuff-things"})

        self.assertEqual(ddl.name(), """`people`.`stuff_things`""")
        self.assertEqual(ddl.name(full=False), """`stuff_things`""")
        self.assertEqual(ddl.name(definition=True), """`people_stuff_things`""")

    def test_create(self):

        ddl = INDEX(name="people", columns=["stuff", "things"])

        ddl.create()
        self.assertEqual(ddl.sql, """INDEX `people` (`stuff`,`things`)""")

        ddl = INDEX(schema="people", table="stuff", name="things", columns=["persons", "stuffins"])

        ddl.create()
        self.assertEqual(ddl.sql, """CREATE INDEX `stuff_things` ON `people`.`stuff` (`persons`,`stuffins`)""")

    def test_add(self):

        ddl = INDEX(name="people", columns=["stuff", "things"], added=True)

        ddl.add()
        self.assertEqual(ddl.sql, """ADD INDEX `people` (`stuff`,`things`)""")

        ddl = INDEX(schema="people", table="stuff", name="things", columns=["persons", "stuffins"], added=True)

        ddl.add()
        self.assertEqual(ddl.sql, """CREATE INDEX `stuff_things` ON `people`.`stuff` (`persons`,`stuffins`)""")

    def test_modify(self):

        ddl = INDEX(name="people", columns=["stuff", "things"], definition={"name": "persons"})

        ddl.modify()
        self.assertEqual(ddl.sql, """MODIFY `persons` TO `people`""")

        ddl = INDEX(schema="people", table="stuff", name="things", columns=["persons", "stuffins"], definition={"name": "persons"})

        ddl.modify()
        self.assertEqual(ddl.sql, """MODIFY `persons` TO `people`.`stuff_things`""")

    def test_drop(self):

        ddl = INDEX(definition={"name": "persons"})

        ddl.drop()
        self.assertEqual(ddl.sql, """DROP INDEX `persons`""")

        ddl = INDEX(definition={"table": {"schema": "people", "name": "stuff"}, "name": "things"})

        ddl.drop()
        self.assertEqual(ddl.sql, """DROP INDEX `people`.`stuff_things`""")

    def test_generate(self):

        ddl = INDEX(name="people", columns=["stuff", "things"])

        ddl.generate()
        self.assertEqual(ddl.sql, """INDEX `people` (`stuff`,`things`)""")
        self.assertEqual(ddl.args, [])

        ddl = INDEX(name="people", columns=["stuff", "things"], added=True)

        ddl.generate()
        self.assertEqual(ddl.sql, """ADD INDEX `people` (`stuff`,`things`)""")
        self.assertEqual(ddl.args, [])

        ddl = INDEX(name="people", columns=["stuff", "things"], definition={"name": "persons"})

        ddl.generate()
        self.assertEqual(ddl.sql, """MODIFY `persons` TO `people`""")
        self.assertEqual(ddl.args, [])

        ddl = INDEX(definition={"name": "persons"})

        ddl.generate()
        self.assertEqual(ddl.sql, """DROP INDEX `persons`""")
        self.assertEqual(ddl.args, [])


class UNIQUE(INDEX):

    CREATE = "UNIQUE"

class TestUNIQUE(unittest.TestCase):

    maxDiff = None

    def test_generate(self):

        ddl = UNIQUE(name="people", columns=["stuff", "things"])

        ddl.generate()
        self.assertEqual(ddl.sql, """UNIQUE `people` (`stuff`,`things`)""")
        self.assertEqual(ddl.args, [])

        ddl = UNIQUE(name="people", columns=["stuff", "things"], added=True)

        ddl.generate()
        self.assertEqual(ddl.sql, """ADD UNIQUE `people` (`stuff`,`things`)""")
        self.assertEqual(ddl.args, [])

        ddl = UNIQUE(name="people", columns=["stuff", "things"], definition={"name": "persons"})

        ddl.generate()
        self.assertEqual(ddl.sql, """MODIFY `persons` TO `people`""")
        self.assertEqual(ddl.args, [])

        ddl = UNIQUE(definition={"name": "persons"})

        ddl.generate()
        self.assertEqual(ddl.sql, """DROP INDEX `persons`""")
        self.assertEqual(ddl.args, [])
