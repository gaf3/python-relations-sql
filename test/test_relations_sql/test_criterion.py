import unittest
import unittest.mock

import test_sql
import test_expression

import relations_sql


class SQL(test_sql.SQL):

    LEFT = test_expression.FIELD
    RIGHT = test_expression.VALUE


class CRITERION(SQL, relations_sql.CRITERION):

    OPERAND = "%s CRIERION %s"
    INVERT = "%s CRIERIOFF %s"

class CRITERIONLY(SQL, relations_sql.CRITERION):

    OPERAND = "%s CRITERIONLY %s"

class TestCRITERION(unittest.TestCase):

    maxDiff = None

    def test___init__(self):

        criterion = CRITERION("totes", "maigoats", jsonify=True)

        self.assertIsInstance(criterion.left, test_expression.FIELD)
        self.assertFalse(criterion.invert)
        self.assertEqual(criterion.left.name, "totes")
        self.assertTrue(criterion.left.jsonify)
        self.assertIsInstance(criterion.right, test_expression.VALUE)
        self.assertEqual(criterion.right.value, "maigoats")
        self.assertTrue(criterion.right.jsonify)

        criterion = CRITERION(test_expression.FIELD("toats"), test_expression.VALUE("maigotes"))

        self.assertIsInstance(criterion.left, test_expression.FIELD)
        self.assertFalse(criterion.invert)
        self.assertEqual(criterion.left.name, "toats")
        self.assertFalse(criterion.left.jsonify)
        self.assertIsInstance(criterion.right, test_expression.VALUE)
        self.assertEqual(criterion.right.value, "maigotes")
        self.assertFalse(criterion.right.jsonify)

        criterion = CRITERION(totes__a="maigoats", invert=True)

        self.assertIsInstance(criterion.left, test_expression.FIELD)
        self.assertTrue(criterion.invert)
        self.assertEqual(criterion.left.name, "totes")
        self.assertEqual(criterion.left.path, ["a"])
        self.assertFalse(criterion.left.jsonify)
        self.assertIsInstance(criterion.right, test_expression.VALUE)
        self.assertEqual(criterion.right.value, "maigoats")
        self.assertTrue(criterion.right.jsonify)

        criterion = CRITERION(totes__a="maigoats", extracted=True)

        self.assertIsInstance(criterion.left, test_expression.FIELD)
        self.assertEqual(criterion.left.name, "totes__a")
        self.assertEqual(criterion.left.path, [])
        self.assertFalse(criterion.left.jsonify)
        self.assertIsInstance(criterion.right, test_expression.VALUE)
        self.assertEqual(criterion.right.value, "maigoats")
        self.assertFalse(criterion.right.jsonify)

        self.assertRaisesRegex(relations_sql.SQLError, "no invert without INVERT operand", CRITERIONLY, invert=True)

    def test___len__(self):

        criterion = CRITERION("totes", "maigoats", jsonify=True)

        self.assertEqual(len(criterion), 2)

    def test_generate(self):

        criterion = CRITERION("totes", "maigoats")

        criterion.generate()
        self.assertEqual(criterion.sql, "`totes` CRIERION %s")
        self.assertEqual(criterion.args, ["maigoats"])

        criterion = CRITERION("totes", "maigoats", invert=True)

        criterion.generate()
        self.assertEqual(criterion.sql, "`totes` CRIERIOFF %s")
        self.assertEqual(criterion.args, ["maigoats"])

        criterion = CRITERION(totes__a="maigoats")

        criterion.generate()
        self.assertEqual(criterion.sql, "`totes`#>>%s CRIERION JSON(%s)")
        self.assertEqual(criterion.args, ['$."a"', '"maigoats"'])


class NULL(SQL, relations_sql.NULL):
    pass

class TestNULL(unittest.TestCase):

    def test___len__(self):

        criterion = NULL("totes", True)

        self.assertEqual(len(criterion), 1)

    def test_generate(self):

        criterion = NULL("totes", True)

        criterion.generate()
        self.assertEqual(criterion.sql, "`totes` IS NULL")
        self.assertEqual(criterion.args, [])

        criterion = NULL(totes__a=False)

        criterion.generate()
        self.assertEqual(criterion.sql, "`totes`#>>%s IS NOT NULL")
        self.assertEqual(criterion.args, ['$."a"'])


class EQ(SQL, relations_sql.EQ):
    pass

class TestEQ(unittest.TestCase):

    def test_generate(self):

        criterion = EQ("totes", "maigoats")

        criterion.generate()
        self.assertEqual(criterion.sql, "`totes`=%s")
        self.assertEqual(criterion.args, ["maigoats"])

        criterion = EQ("totes", "maigoats", invert=True)

        criterion.generate()
        self.assertEqual(criterion.sql, "`totes`!=%s")
        self.assertEqual(criterion.args, ["maigoats"])

        criterion = EQ(totes__a="maigoats")

        criterion.generate()
        self.assertEqual(criterion.sql, "`totes`#>>%s=JSON(%s)")
        self.assertEqual(criterion.args, ['$."a"', '"maigoats"'])


class GT(SQL, relations_sql.GT):
    pass

class TestGT(unittest.TestCase):

    def test_generate(self):

        criterion = GT("totes", "maigoats")

        criterion.generate()
        self.assertEqual(criterion.sql, "`totes`>%s")
        self.assertEqual(criterion.args, ["maigoats"])

        criterion = GT(totes__a="maigoats")

        criterion.generate()
        self.assertEqual(criterion.sql, "`totes`#>>%s>JSON(%s)")
        self.assertEqual(criterion.args, ['$."a"', '"maigoats"'])


class GTE(SQL, relations_sql.GTE):
    pass

class TestGTE(unittest.TestCase):

    def test_generate(self):

        criterion = GTE("totes", "maigoats")

        criterion.generate()
        self.assertEqual(criterion.sql, "`totes`>=%s")
        self.assertEqual(criterion.args, ["maigoats"])

        criterion = GTE(totes__a="maigoats")

        criterion.generate()
        self.assertEqual(criterion.sql, "`totes`#>>%s>=JSON(%s)")
        self.assertEqual(criterion.args, ['$."a"', '"maigoats"'])


class LT(SQL, relations_sql.LT):
    pass

class TestLT(unittest.TestCase):

    def test_generate(self):

        criterion = LT("totes", "maigoats")

        criterion.generate()
        self.assertEqual(criterion.sql, "`totes`<%s")
        self.assertEqual(criterion.args, ["maigoats"])

        criterion = LT(totes__a="maigoats")

        criterion.generate()
        self.assertEqual(criterion.sql, "`totes`#>>%s<JSON(%s)")
        self.assertEqual(criterion.args, ['$."a"', '"maigoats"'])


class LTE(SQL, relations_sql.LTE):
    pass

class TestLTE(unittest.TestCase):

    def test_generate(self):

        criterion = LTE("totes", "maigoats")

        criterion.generate()
        self.assertEqual(criterion.sql, "`totes`<=%s")
        self.assertEqual(criterion.args, ["maigoats"])

        criterion = LTE(totes__a="maigoats")

        criterion.generate()
        self.assertEqual(criterion.sql, "`totes`#>>%s<=JSON(%s)")
        self.assertEqual(criterion.args, ['$."a"', '"maigoats"'])


class LIKE(SQL, relations_sql.LIKE):
    pass

class TestLIKE(unittest.TestCase):

    def test_generate(self):

        criterion = LIKE("totes", "maigoats")

        criterion.generate()
        self.assertEqual(criterion.sql, "`totes` LIKE %s")
        self.assertEqual(criterion.args, ["%maigoats%"])

        criterion = LIKE("totes", "maigoats", invert=True)

        criterion.generate()
        self.assertEqual(criterion.sql, "`totes` NOT LIKE %s")
        self.assertEqual(criterion.args, ["%maigoats%"])

        criterion = LIKE(totes__a="maigoats")

        criterion.generate()
        self.assertEqual(criterion.sql, "`totes`#>>%s LIKE JSON(%s)")
        self.assertEqual(criterion.args, ['$."a"', '"%maigoats%"'])


class START(SQL, relations_sql.START):
    pass

class TestSTART(unittest.TestCase):

    def test_generate(self):

        criterion = START("totes", "maigoats")

        criterion.generate()
        self.assertEqual(criterion.sql, "`totes` LIKE %s")
        self.assertEqual(criterion.args, ["maigoats%"])

        criterion = START("totes", "maigoats", invert=True)

        criterion.generate()
        self.assertEqual(criterion.sql, "`totes` NOT LIKE %s")
        self.assertEqual(criterion.args, ["maigoats%"])

        criterion = START(totes__a="maigoats")

        criterion.generate()
        self.assertEqual(criterion.sql, "`totes`#>>%s LIKE JSON(%s)")
        self.assertEqual(criterion.args, ['$."a"', '"maigoats%"'])


class END(SQL, relations_sql.END):
    pass

class TestEND(unittest.TestCase):

    def test_generate(self):

        criterion = END("totes", "maigoats")

        criterion.generate()
        self.assertEqual(criterion.sql, "`totes` LIKE %s")
        self.assertEqual(criterion.args, ["%maigoats"])

        criterion = END("totes", "maigoats", invert=True)

        criterion.generate()
        self.assertEqual(criterion.sql, "`totes` NOT LIKE %s")
        self.assertEqual(criterion.args, ["%maigoats"])

        criterion = END(totes__a="maigoats")

        criterion.generate()
        self.assertEqual(criterion.sql, "`totes`#>>%s LIKE JSON(%s)")
        self.assertEqual(criterion.args, ['$."a"', '"%maigoats"'])


class IN(SQL, relations_sql.IN):

    RIGHT = test_expression.LIST
    VALUE = test_expression.VALUE

class TestIN(unittest.TestCase):

    def test_generate(self):

        criterion = IN("totes", ["mai", "goats"])

        criterion.generate()
        self.assertEqual(criterion.sql, "`totes` IN (%s,%s)")
        self.assertEqual(criterion.args, ["mai", "goats"])

    def test_generate(self):

        criterion = IN("totes", ["mai", "goats"])

        criterion.generate()
        self.assertEqual(criterion.sql, "`totes` IN (%s,%s)")
        self.assertEqual(criterion.args, ["mai", "goats"])

        criterion = IN("totes", ["mai", "goats"], invert=True)

        criterion.generate()
        self.assertEqual(criterion.sql, "`totes` NOT IN (%s,%s)")
        self.assertEqual(criterion.args, ["mai", "goats"])

        criterion = IN(totes__a=["mai", "goats"])

        criterion.generate()
        self.assertEqual(criterion.sql, "`totes`#>>%s IN (JSON(%s),JSON(%s))")
        self.assertEqual(criterion.args, ['$."a"', '"mai"', '"goats"'])

        criterion = IN(totes__a=[])

        criterion.generate()
        self.assertEqual(criterion.sql, "%s")
        self.assertEqual(criterion.args, [False])


class CONTAINS(SQL, relations_sql.CONTAINS):

    OPERAND = "CONTAINS(%s,%s)"

class TestCONTAINS(unittest.TestCase):

    def test_generate(self):

        criterion = CONTAINS("totes", ["mai", "goats"])

        criterion.generate()
        self.assertEqual(criterion.sql, "CONTAINS(`totes`,JSON(%s))")
        self.assertEqual(criterion.args, ['["mai", "goats"]'])


class LENGTHS(SQL, relations_sql.LENGTHS):

    OPERAND = "LENGTHS(%s,%s)"

class TestLENGTHS(unittest.TestCase):

    def test_generate(self):

        criterion = LENGTHS("totes", ["mai", "goats"])

        criterion.generate()
        self.assertEqual(criterion.sql, "LENGTHS(`totes`,JSON(%s))")
        self.assertEqual(criterion.args, ['["mai", "goats"]'])
