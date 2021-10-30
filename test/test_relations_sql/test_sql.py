import unittest
import unittest.mock

import relations_sql


class SQL:

    QUOTE = '`'
    STR = "'"
    SEPARATOR = '.'
    PLACEHOLDER = "%s"
    JSONIFY = "JSON(%s)"
    PATH = "%s#>>%s"

    @staticmethod
    def walk(path):

        places = []

        for place in path:
            if isinstance(place, int):
                places.append(f"[{int(place)}]")
            else:
                places.append(f'."{place}"')

        return f"${''.join(places)}"


class TestSQLError(unittest.TestCase):

    maxDiff = None

    def test___init__(self):

        error = relations_sql.SQLError("unittest", "oops")

        self.assertEqual(error.sql, """unittest""")
        self.assertEqual(error.message, "oops")


class TestSQL(unittest.TestCase):

    maxDiff = None

    def test___init__(self):

        sql = relations_sql.SQL("unit", "test")

        self.assertEqual(sql.sql, """unit""")
        self.assertEqual(sql.args, "test")

    def test___len__(self):

        sql = relations_sql.SQL()
        self.assertEqual(len(sql), 0)

        sql.sql = True
        self.assertEqual(len(sql), 1)

    def test_generate(self):

        sql = relations_sql.SQL()
        sql.generate()
