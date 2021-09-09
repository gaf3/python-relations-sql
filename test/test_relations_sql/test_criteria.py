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

    def test_generate(self):

        criteria = SPACE()
        self.assertFalse(criteria.generate())

        criteria("people", "stuff", "things")
        criteria.generate()
        self.assertEqual(criteria.sql, "people stuff things")
        self.assertEqual(criteria.args, [])

        criteria = LOGIC()
        self.assertFalse(criteria.generate())

        criteria(test_criterion.EQ("totes", "maigoats"), test_criterion.EQ("toast", "myghost", invert=True))
        criteria.generate()
        self.assertEqual(criteria.sql, "(`totes`=%s LOGIC `toast`!=%s)")
        self.assertEqual(criteria.args, ["maigoats", "myghost"])

        criteria.generate(indent=2)
        self.assertEqual(criteria.sql, """(
  `totes`=%s LOGIC
  `toast`!=%s
)""")

        criteria.generate(indent=2, count=1)
        self.assertEqual(criteria.sql, """(
    `totes`=%s LOGIC
    `toast`!=%s
  )""")

        criteria.generate(indent=2, count=2)
        self.assertEqual(criteria.sql, """(
      `totes`=%s LOGIC
      `toast`!=%s
    )""")

        criteria = LOGIC()
        criteria(LOGIC(test_criterion.EQ("totes", "maigoats"), test_criterion.EQ("toast", "myghost", invert=True)))
        criteria(LOGIC(test_criterion.EQ("totes", "maigoats"), test_criterion.EQ("toast", "myghost", invert=True)))

        criteria.generate(indent=2)
        self.assertEqual(criteria.sql, """(
  (
    `totes`=%s LOGIC
    `toast`!=%s
  ) LOGIC
  (
    `totes`=%s LOGIC
    `toast`!=%s
  )
)""")

        criteria.generate(indent=2, count=1)
        self.assertEqual(criteria.sql, """(
    (
      `totes`=%s LOGIC
      `toast`!=%s
    ) LOGIC
    (
      `totes`=%s LOGIC
      `toast`!=%s
    )
  )""")

        criteria.generate(indent=2, count=2)
        self.assertEqual(criteria.sql, """(
      (
        `totes`=%s LOGIC
        `toast`!=%s
      ) LOGIC
      (
        `totes`=%s LOGIC
        `toast`!=%s
      )
    )""")

class AND(relations_sql.AND):

    ARGS = test_expression.VALUE

class TestAND(unittest.TestCase):

    maxDiff = None

    def test_generate(self):

        criteria = AND(test_criterion.EQ("totes", "maigoats"), test_criterion.EQ("toast", "myghost", invert=True))
        criteria.generate()
        self.assertEqual(criteria.sql, "(`totes`=%s AND `toast`!=%s)")
        self.assertEqual(criteria.args, ["maigoats", "myghost"])

        criteria.generate(indent=2)
        self.assertEqual(criteria.sql, """(
  `totes`=%s AND
  `toast`!=%s
)""")

        criteria.generate(indent=2, count=1)
        self.assertEqual(criteria.sql, """(
    `totes`=%s AND
    `toast`!=%s
  )""")

        criteria.generate(indent=2, count=2)
        self.assertEqual(criteria.sql, """(
      `totes`=%s AND
      `toast`!=%s
    )""")


class OR(relations_sql.OR):

    ARGS = test_expression.VALUE

class TestOR(unittest.TestCase):

    maxDiff = None

    def test_generate(self):

        criteria = OR(test_criterion.EQ("totes", "maigoats"), test_criterion.EQ("toast", "myghost", invert=True))
        criteria.generate()
        self.assertEqual(criteria.sql, "(`totes`=%s OR `toast`!=%s)")
        self.assertEqual(criteria.args, ["maigoats", "myghost"])

        criteria.generate(indent=2)
        self.assertEqual(criteria.sql, """(
  `totes`=%s OR
  `toast`!=%s
)""")

        criteria.generate(indent=2, count=1)
        self.assertEqual(criteria.sql, """(
    `totes`=%s OR
    `toast`!=%s
  )""")

        criteria.generate(indent=2, count=2)
        self.assertEqual(criteria.sql, """(
      `totes`=%s OR
      `toast`!=%s
    )""")


class SETS(test_criterion.SQL, relations_sql.SETS):

    def __init__(self, left=None, right=None, jsonify=False, **kwargs):

        super().__init__(left, right, jsonify, **kwargs)

        self.expression = AND(self.left, self.right)

class TestSETS(unittest.TestCase):

    def test_generate(self):

        criteria = SETS("totes", ["mai", "goats"])

        criteria.generate()
        self.assertEqual(criteria.sql, "(`totes` AND JSON(%s))")
        self.assertEqual(criteria.args, ['["mai", "goats"]'])


class HAS(test_criterion.SQL, relations_sql.HAS):

    CONTAINS = test_criterion.CONTAINS

class TestHAS(unittest.TestCase):

    def test___init__(self):

        criteria = HAS("totes", ["mai", "goats"])

        self.assertIsInstance(criteria.expression, test_criterion.CONTAINS)
        self.assertIsInstance(criteria.expression.left, test_expression.FIELD)
        self.assertIsInstance(criteria.expression.right, test_expression.VALUE)
        self.assertEqual(criteria.expression.left.name, "totes")
        self.assertEqual(criteria.expression.right.value, ["mai", "goats"])

        criteria = HAS(totes=["mai", "goats"])

        self.assertIsInstance(criteria.expression, test_criterion.CONTAINS)
        self.assertIsInstance(criteria.expression.left, test_expression.FIELD)
        self.assertIsInstance(criteria.expression.right, test_expression.VALUE)
        self.assertEqual(criteria.expression.left.name, "totes")
        self.assertEqual(criteria.expression.right.value, ["mai", "goats"])

    def test___len__(self):

        criteria = HAS("totes", ["mai", "goats"])

        self.assertEqual(len(criteria), 1)

    def test_generate(self):

        criteria = HAS("totes", ["mai", "goats"])

        criteria.generate()
        self.assertEqual(criteria.sql, "CONTAINS(`totes`,JSON(%s))")
        self.assertEqual(criteria.args, ['["mai", "goats"]'])


class ANY(test_criterion.SQL, relations_sql.ANY):

    OR = OR
    LEFT = test_expression.FIELD
    VALUE = test_expression.VALUE
    CONTAINS = test_criterion.CONTAINS

class TestANY(unittest.TestCase):

    def test___init__(self):

        criteria = ANY("totes", ["mai", "goats"])

        self.assertIsInstance(criteria.expression, OR)
        self.assertIsInstance(criteria.expression.expressions[0], test_criterion.CONTAINS)
        self.assertIsInstance(criteria.expression.expressions[1], test_criterion.CONTAINS)
        self.assertIsInstance(criteria.expression.expressions[0].left, test_expression.FIELD)
        self.assertIsInstance(criteria.expression.expressions[0].right, test_expression.VALUE)
        self.assertIsInstance(criteria.expression.expressions[1].left, test_expression.FIELD)
        self.assertIsInstance(criteria.expression.expressions[1].right, test_expression.VALUE)
        self.assertEqual(criteria.expression.expressions[0].left.name, "totes")
        self.assertEqual(criteria.expression.expressions[0].right.value, ["mai"])
        self.assertEqual(criteria.expression.expressions[1].left.name, "totes")
        self.assertEqual(criteria.expression.expressions[1].right.value, ["goats"])

        criteria = ANY(totes=["mai", "goats"])

        self.assertIsInstance(criteria.expression, OR)
        self.assertIsInstance(criteria.expression.expressions[0], test_criterion.CONTAINS)
        self.assertIsInstance(criteria.expression.expressions[1], test_criterion.CONTAINS)
        self.assertIsInstance(criteria.expression.expressions[0].left, test_expression.FIELD)
        self.assertIsInstance(criteria.expression.expressions[0].right, test_expression.VALUE)
        self.assertIsInstance(criteria.expression.expressions[1].left, test_expression.FIELD)
        self.assertIsInstance(criteria.expression.expressions[1].right, test_expression.VALUE)
        self.assertEqual(criteria.expression.expressions[0].left.name, "totes")
        self.assertEqual(criteria.expression.expressions[0].right.value, ["mai"])
        self.assertEqual(criteria.expression.expressions[1].left.name, "totes")
        self.assertEqual(criteria.expression.expressions[1].right.value, ["goats"])

        self.assertRaisesRegex(relations_sql.SQLError, "must be list", ANY, totes="mai goats")

    def test_generate(self):

        criteria = ANY("totes", ["mai", "goats"])

        criteria.generate()
        self.assertEqual(criteria.sql, "(CONTAINS(`totes`,JSON(%s)) OR CONTAINS(`totes`,JSON(%s)))")
        self.assertEqual(criteria.args, ['["mai"]', '["goats"]'])


class ALL(test_criterion.SQL, relations_sql.ALL):

    AND = AND
    CONTAINS = test_criterion.CONTAINS
    LENGTHS = test_criterion.LENGTHS

class TestALL(unittest.TestCase):

    def test___init__(self):

        criteria = ALL("totes", ["mai", "goats"])

        self.assertIsInstance(criteria.expression, AND)
        self.assertIsInstance(criteria.expression.expressions[0], test_criterion.CONTAINS)
        self.assertIsInstance(criteria.expression.expressions[1], test_criterion.LENGTHS)
        self.assertIsInstance(criteria.expression.expressions[0].left, test_expression.FIELD)
        self.assertIsInstance(criteria.expression.expressions[0].right, test_expression.VALUE)
        self.assertIsInstance(criteria.expression.expressions[1].left, test_expression.FIELD)
        self.assertIsInstance(criteria.expression.expressions[1].right, test_expression.VALUE)
        self.assertEqual(criteria.expression.expressions[0].left.name, "totes")
        self.assertEqual(criteria.expression.expressions[0].right.value, ["mai", "goats"])
        self.assertEqual(criteria.expression.expressions[1].left.name, "totes")
        self.assertEqual(criteria.expression.expressions[1].right.value, ["mai", "goats"])

        criteria = ALL(totes=["mai", "goats"])

        self.assertIsInstance(criteria.expression, AND)
        self.assertIsInstance(criteria.expression.expressions[0], test_criterion.CONTAINS)
        self.assertIsInstance(criteria.expression.expressions[1], test_criterion.LENGTHS)
        self.assertIsInstance(criteria.expression.expressions[0].left, test_expression.FIELD)
        self.assertIsInstance(criteria.expression.expressions[0].right, test_expression.VALUE)
        self.assertIsInstance(criteria.expression.expressions[1].left, test_expression.FIELD)
        self.assertIsInstance(criteria.expression.expressions[1].right, test_expression.VALUE)
        self.assertEqual(criteria.expression.expressions[0].left.name, "totes")
        self.assertEqual(criteria.expression.expressions[0].right.value, ["mai", "goats"])
        self.assertEqual(criteria.expression.expressions[1].left.name, "totes")
        self.assertEqual(criteria.expression.expressions[1].right.value, ["mai", "goats"])

    def test_generate(self):

        criteria = ALL("totes", ["mai", "goats"])

        criteria.generate()
        self.assertEqual(criteria.sql, "(CONTAINS(`totes`,JSON(%s)) AND LENGTHS(`totes`,JSON(%s)))")
        self.assertEqual(criteria.args, ['["mai", "goats"]', '["mai", "goats"]'])


class OP(test_criterion.SQL, relations_sql.OP):

    CRITERIONS = {
        'null': test_criterion.NULL,
        'eq': test_criterion.EQ,
        'gt': test_criterion.GT,
        'gte': test_criterion.GTE,
        'lt': test_criterion.LT,
        'lte': test_criterion.LTE,
        'like': test_criterion.LIKE,
        'start': test_criterion.START,
        'end': test_criterion.END,
        'in': test_criterion.IN,
        "has": HAS,
        "any": ANY,
        "all": ALL
    }

class TestOP(unittest.TestCase):

    def test___new__(self):

        criteria = OP("totes__null", True)

        criteria.generate()
        self.assertEqual(criteria.sql, "`totes` IS NULL")
        self.assertEqual(criteria.args, [])

        criteria = OP(totes__a__null=False)

        criteria.generate()
        self.assertEqual(criteria.sql, "`totes`#>>%s IS NOT NULL")
        self.assertEqual(criteria.args, ['$."a"'])

        criteria = OP(totes__a__not_null=True)

        criteria.generate()
        self.assertEqual(criteria.sql, "`totes`#>>%s IS NOT NULL")
        self.assertEqual(criteria.args, ['$."a"'])

        criteria = OP(totes__a__not_has=[1, 2, 3])

        criteria.generate()
        self.assertEqual(criteria.sql, "NOT CONTAINS(`totes`#>>%s,JSON(%s))")
        self.assertEqual(criteria.args, ['$."a"', '[1, 2, 3]'])

        criteria = OP(totes=1, JSONIFY=True)

        criteria.generate()
        self.assertEqual(criteria.sql, "JSON(`totes`)=JSON(%s)")
        self.assertEqual(criteria.args, ['1'])

        self.assertRaisesRegex(relations_sql.SQLError, "need single pair", OP, "nope")

        criteria = OP(totes__a__null=False, EXTRACTED=True)

        criteria.generate()
        self.assertEqual(criteria.sql, "`totes__a` IS NOT NULL")
        self.assertEqual(criteria.args, [])

        self.assertRaisesRegex(relations_sql.SQLError, "need single pair", OP, "nope")
