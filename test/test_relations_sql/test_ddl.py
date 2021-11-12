import unittest
import unittest.mock

import test_sql
import test_expression

import relations
import relations_sql


class SQL(test_sql.SQL):

    STR = "'"


class DDL(SQL, relations_sql.DDL):
    pass

class TestDDL(unittest.TestCase):

    maxDiff = None

    def test___init__(self):

        ddl = DDL(migration={"name": "good"}, definition={"name": "bad"}, added=True)

        self.assertEqual(ddl.STR, "'")
        self.assertEqual(ddl.migration["name"], 'good')
        self.assertEqual(ddl.migration["store"], 'good')
        self.assertEqual(ddl.definition["name"], 'bad')
        self.assertEqual(ddl.definition["store"], 'bad')
        self.assertTrue(ddl.added)

        ddl = DDL(name="ugly")
        self.assertEqual(ddl.migration, {"name": "ugly", "store": "ugly"})

    def test___len__(self):

        ddl = DDL()

        self.assertEqual(len(ddl), 1)

    def test_str(self):

        ddl = DDL()

        self.assertEqual(ddl.str(1), "'1'")

    def test_generate(self):

        ddl = DDL()

        ddl.create = unittest.mock.MagicMock()
        ddl.add = unittest.mock.MagicMock()
        ddl.modify = unittest.mock.MagicMock()
        ddl.drop = unittest.mock.MagicMock()

        ddl.migration = True
        ddl.generate()
        ddl.create.assert_called_once_with()

        ddl.added = True
        ddl.generate()
        ddl.add.assert_called_once_with()

        ddl.definition = True
        ddl.generate()
        ddl.add.assert_called_once_with()
        ddl.modify.assert_called_once_with()

        ddl.migration = None
        ddl.generate()
        ddl.add.assert_called_once_with()
        ddl.modify.assert_called_once_with()
        ddl.drop.assert_called_once_with()
