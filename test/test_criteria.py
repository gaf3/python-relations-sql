import unittest
import unittest.mock

import test_expression
import test_criterion

import relations_sql


class SPACE(relations_sql.CRITERIA):

    ARGS = relations_sql.SQL

    DELIMITTER = " "
    PARENTHESES = False

class LOGIC(relations_sql.CRITERIA):

    ARGS = test_expression.VALUE
    KWARGS = test_criterion.OP

    DELIMITTER = " LOGIC "

class ALIAS(relations_sql.CRITERIA):

    ARGS = test_expression.FIELD
    KWARG = test_expression.FIELD
    KWARGS = test_expression.AS

    DELIMITTER = " ALIAS "
    PARENTHESES = False

class TestCRITERIA(unittest.TestCase):

    maxDiff = None

    def test___init__(self):

        criteria = SPACE("people")

        self.assertEqual(len(criteria.expressions), 1)
        self.assertIsInstance(criteria.expressions[0], relations_sql.SQL)
        self.assertEqual(criteria.expressions[0].sql, "people")

        criteria = LOGIC("stuff")

        self.assertEqual(len(criteria.expressions), 1)
        self.assertIsInstance(criteria.expressions[0], test_expression.VALUE)
        self.assertEqual(criteria.expressions[0].value, "stuff")

        criteria = ALIAS("things")

        self.assertEqual(len(criteria.expressions), 1)
        self.assertIsInstance(criteria.expressions[0], test_expression.FIELD)
        self.assertEqual(criteria.expressions[0].name, "things")

    def test___call__(self):

        criteria = SPACE()

        criteria("people")
        self.assertEqual(len(criteria.expressions), 1)
        self.assertIsInstance(criteria.expressions[0], relations_sql.SQL)
        self.assertEqual(criteria.expressions[0].sql, "people")

        criteria = LOGIC()

        criteria("stuff")
        self.assertEqual(len(criteria.expressions), 1)
        self.assertIsInstance(criteria.expressions[0], test_expression.VALUE)
        self.assertEqual(criteria.expressions[0].value, "stuff")

        criteria = ALIAS()

        criteria("things")
        self.assertEqual(len(criteria.expressions), 1)
        self.assertIsInstance(criteria.expressions[0], test_expression.FIELD)
        self.assertEqual(criteria.expressions[0].name, "things")

    def test_add(self):

        criteria = SPACE()

        criteria.add("people")
        self.assertEqual(len(criteria.expressions), 1)
        self.assertIsInstance(criteria.expressions[0], relations_sql.SQL)
        self.assertEqual(criteria.expressions[0].sql, "people")

        criteria = LOGIC()

        criteria.add(False)
        self.assertEqual(len(criteria.expressions), 1)
        self.assertIsInstance(criteria.expressions[0], test_expression.VALUE)
        self.assertFalse(criteria.expressions[0].value)

        criteria.add([test_criterion.EQ("totes", "maigoats")])
        self.assertEqual(len(criteria.expressions), 2)
        self.assertIsInstance(criteria.expressions[1], test_criterion.EQ)
        self.assertEqual(criteria.expressions[1].left.name, "totes")
        self.assertEqual(criteria.expressions[1].right.value, "maigoats")

        criteria.add(totes__a__null=False)
        self.assertEqual(len(criteria.expressions), 3)
        self.assertIsInstance(criteria.expressions[2], test_criterion.NULL)
        self.assertEqual(criteria.expressions[2].left.name, "totes")
        self.assertEqual(criteria.expressions[2].left.path, ["a"])
        self.assertFalse(criteria.expressions[2].right.value)

        criteria = ALIAS()

        criteria.add("people")
        self.assertEqual(len(criteria.expressions), 1)
        self.assertIsInstance(criteria.expressions[0], test_expression.FIELD)
        self.assertEqual(criteria.expressions[0].name, "people")

        criteria.add([test_expression.AS("totes", "maigoats")])
        self.assertEqual(len(criteria.expressions), 2)
        self.assertIsInstance(criteria.expressions[1], test_expression.AS)
        self.assertEqual(criteria.expressions[1].label.name, "totes")
        self.assertEqual(criteria.expressions[1].expression, "maigoats")

        criteria.add(stuff="things")
        self.assertEqual(len(criteria.expressions), 3)
        self.assertIsInstance(criteria.expressions[2], test_expression.AS)
        self.assertIsInstance(criteria.expressions[2].label, test_expression.NAME)
        self.assertIsInstance(criteria.expressions[2].expression, test_expression.FIELD)
        self.assertEqual(criteria.expressions[2].label.name, "stuff")
        self.assertEqual(criteria.expressions[2].expression.name, "things")

    def test_generate(self):

        criteria = SPACE()
        self.assertFalse(criteria.generate())

        criteria("people", "stuff", "things")
        criteria.generate()
        self.assertEqual(criteria.sql, "people stuff things")
        self.assertEqual(criteria.args, [])

        criteria = LOGIC()
        self.assertFalse(criteria.generate())

        criteria(test_criterion.EQ("totes", "maigoats"), totes__a__null=False)
        criteria.generate()
        self.assertEqual(criteria.sql, "(`totes`=%s LOGIC `totes`>%s IS NOT NULL)")
        self.assertEqual(criteria.args, ["maigoats", '$."a"'])

        criteria = ALIAS("people", stuff="things")
        criteria.generate()
        self.assertEqual(criteria.sql, "`people` ALIAS `things` AS `stuff`")
        self.assertEqual(criteria.args, [])


class AND(relations_sql.AND):

    ARGS = test_expression.VALUE
    KWARGS = test_criterion.OP

class TestAND(unittest.TestCase):

    maxDiff = None

    def test_generate(self):

        criteria = AND(test_criterion.EQ("totes", "maigoats"), totes__a__null=False)
        criteria.generate()
        self.assertEqual(criteria.sql, "(`totes`=%s AND `totes`>%s IS NOT NULL)")
        self.assertEqual(criteria.args, ["maigoats", '$."a"'])


class OR(relations_sql.OR):

    ARGS = test_expression.VALUE
    KWARGS = test_criterion.OP

class TestOR(unittest.TestCase):

    maxDiff = None

    def test_generate(self):

        criteria = OR(test_criterion.EQ("totes", "maigoats"), totes__a__null=False)
        criteria.generate()
        self.assertEqual(criteria.sql, "(`totes`=%s OR `totes`>%s IS NOT NULL)")
        self.assertEqual(criteria.args, ["maigoats", '$."a"'])
