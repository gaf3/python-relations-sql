import unittest
import unittest.mock

import test_expression
import test_criterion
import test_clause

import collections

import relations_sql


class STATEMENT(relations_sql.STATEMENT):

    NAME = "STATEMENT"

    CLAUSES = collections.OrderedDict([
        ("SELECT", test_clause.FIELDS),
        ("FROM", test_clause.FROM)
    ])

class TestSTATEMENT(unittest.TestCase):

    maxDiff = None

    def test___init__(self):

        statement = STATEMENT()

        self.assertEqual(statement.SELECT.expressions, [])
        self.assertEqual(statement.FROM.expressions, [])

        statement = STATEMENT(SELECT="people.stuff", FROM=test_clause.FROM("things"))

        self.assertEqual(statement.SELECT.expressions[0].table.name, "people")
        self.assertEqual(statement.SELECT.expressions[0].name, "stuff")
        self.assertEqual(statement.FROM.expressions[0].name, "things")

        self.assertRaisesRegex(TypeError, "'nope' is an invalid keyword argument for STATEMENT", STATEMENT, nope=False)

    def test___getattr__(self):

        model = unittest.mock.MagicMock()
        statement = STATEMENT(SELECT="people.stuff", FROM="things").bind(model)

        statement.retrieve(False)

        model.retrieve.assert_called_once_with(False)

        def nope():

            statement.nope

        self.assertRaisesRegex(AttributeError, "object has no attribute", nope)

    def test___len__(self):

        statement = STATEMENT(SELECT="people.stuff", FROM="things")

        self.assertEqual(len(statement), 2)

    def test_check(self):

        statement = STATEMENT(SELECT="people.stuff", FROM="things")

        statement.check({})
        self.assertEqual(statement.clauses, {})

        self.assertRaisesRegex(TypeError, "'nope' is an invalid keyword argument for STATEMENT", STATEMENT, nope=False)

    def test_bind(self):

        model = unittest.mock.MagicMock()
        statement = STATEMENT(SELECT="people.stuff", FROM="things").bind(model)

        self.assertEqual(statement.model, model)

    def test_generate(self):

        statement = STATEMENT(SELECT="people.stuff", FROM="things")

        statement.generate()
        self.assertEqual(statement.sql, "STATEMENT `people`.`stuff` FROM `things`")
        self.assertEqual(statement.args, [])


ASC = test_expression.ASC
DESC = test_expression.DESC

class SELECT(relations_sql.SELECT):

    CLAUSES = collections.OrderedDict([
        ("OPTIONS", test_clause.OPTIONS),
        ("FIELDS", test_clause.FIELDS),
        ("FROM", test_clause.FROM),
        ("WHERE", test_clause.WHERE),
        ("GROUP_BY", test_clause.GROUP_BY),
        ("HAVING", test_clause.HAVING),
        ("ORDER_BY", test_clause.ORDER_BY),
        ("LIMIT", test_clause.LIMIT)
    ])

class TestSELECT(unittest.TestCase):

    maxDiff = None

    def test___init__(self):

        statement = SELECT("*").FROM("people").WHERE(stuff__gt="things")

        self.assertEqual(statement.FIELDS.expressions[0].name, "*")
        self.assertEqual(statement.FROM.expressions[0].name, "people")
        self.assertIsInstance(statement.WHERE.expressions[0], test_criterion.GT)
        self.assertEqual(statement.WHERE.expressions[0].left.name, "stuff")
        self.assertEqual(statement.WHERE.expressions[0].right.value, "things")

    def test_generate(self):

        statement = SELECT("*").OPTIONS("FAST").FROM("people").WHERE(stuff__gt="things")

        statement.generate()
        self.assertEqual(statement.sql, "SELECT FAST * FROM `people` WHERE `stuff`>%s")
        self.assertEqual(statement.args, ["things"])

        statement = SELECT(
            "*"
        ).FROM(
            people=SELECT(
                "a.b.c"
            ).FROM(
                "d.e"
            )
        ).WHERE(
            stuff__in=SELECT(
                "f"
            ).FROM(
                "g"
            ).WHERE(
                things__a__0___1____2_____3__gt=5
            )
        )

        statement.generate()
        self.assertEqual(statement.sql,
            "SELECT * FROM (SELECT `a`.`b`.`c` FROM `d`.`e`) "
            "AS `people` WHERE `stuff` IN "
            "(SELECT `f` FROM `g` WHERE `things`>%s>JSON(%s))"
        )
        self.assertEqual(statement.args, ['$."a"[0][-1]."2"."-3"', '5'])

        statement.GROUP_BY("fee", "fie").HAVING(foe="fum").ORDER_BY("yin", yang=DESC).LIMIT(1, 2)

        statement.generate()
        self.assertEqual(statement.sql,
            "SELECT * FROM (SELECT `a`.`b`.`c` FROM `d`.`e`) "
            "AS `people` WHERE `stuff` IN "
            "(SELECT `f` FROM `g` WHERE `things`>%s>JSON(%s)) "
            "GROUP BY `fee`,`fie` HAVING `foe`=%s "
            "ORDER BY `yin`,`yang` DESC LIMIT %s,%s"
        )
        self.assertEqual(statement.args, ['$."a"[0][-1]."2"."-3"', '5', 'fum', 1, 2])


class INSERT(relations_sql.INSERT):

    CLAUSES = collections.OrderedDict([
        ("OPTIONS", test_clause.OPTIONS),
        ("TABLE", test_expression.TABLE),
        ("FIELDS", test_expression.NAMES),
        ("VALUES", test_clause.VALUES),
        ("SELECT", SELECT)
    ])

class TestINSERT(unittest.TestCase):

    maxDiff = None

    def test___init__(self):

        statement = INSERT("people.stuff", "things", SELECT="*")

        self.assertEqual(statement.TABLE.name, "stuff")
        self.assertEqual(statement.TABLE.schema.name, "people")
        self.assertEqual(statement.FIELDS.expressions[0].name, "things")
        self.assertEqual(statement.SELECT.FIELDS.expressions[0].name, "*")

        statement = INSERT("people.stuff", FIELDS=["things"], SELECT=SELECT("stuff").FROM("things"))

        self.assertEqual(statement.TABLE.name, "stuff")
        self.assertEqual(statement.TABLE.schema.name, "people")
        self.assertEqual(statement.FIELDS.expressions[0].name, "things")

        self.assertRaisesRegex(TypeError, "'nope' is an invalid keyword argument for INSERT", INSERT, "table", nope=False)

    def test_field(self):

        statement = INSERT("people.stuff")

        statement.field(["things"])
        self.assertEqual(statement.FIELDS.expressions[0].name, "things")

        statement.field(["thingies"])
        self.assertEqual(statement.FIELDS.expressions[0].name, "things")

    def test_generate(self):

        statement = INSERT("people").VALUES(stuff=1, things=2).VALUES(3, 4)

        statement.generate()
        self.assertEqual(statement.sql,"INSERT INTO `people` (`stuff`,`things`) VALUES (%s,%s),(%s,%s)")
        self.assertEqual(statement.args, [1, 2, 3, 4])

        statement = INSERT("people").OPTIONS("FAST")
        statement.SELECT("stuff").FROM("things")

        statement.generate()
        self.assertEqual(statement.sql,"INSERT FAST INTO `people` SELECT `stuff` FROM `things`")
        self.assertEqual(statement.args, [])

        statement = INSERT("people").VALUES(stuff=1, things=2).VALUES(3, 4)
        statement.SELECT("stuff").FROM("things")

        self.assertRaisesRegex(relations_sql.SQLError, "set VALUES or SELECT but not both", statement.generate)


class LIMITED(relations_sql.LIMITED):

    NAME = "LIMITED"

    CLAUSES = collections.OrderedDict([
        ("TABLE", test_expression.TABLE),
        ("SELECT", test_clause.FIELDS),
        ("LIMIT", test_clause.LIMIT)
    ])

class TestLIMITED(unittest.TestCase):

    maxDiff = None

    def test___init__(self):

        statement = LIMITED("people", SELECT="*")

        self.assertEqual(statement.SELECT.expressions[0].name, "*")
        self.assertEqual(statement.TABLE.name, "people")

        statement = LIMITED("people", SELECT=test_clause.FIELDS("*"))

        self.assertEqual(statement.SELECT.expressions[0].name, "*")
        self.assertEqual(statement.TABLE.name, "people")

        statement = LIMITED("people")

        self.assertEqual(statement.SELECT.expressions, [])
        self.assertEqual(statement.TABLE.name, "people")

        self.assertRaisesRegex(TypeError, "'nope' is an invalid keyword argument for INSERT", INSERT, "table", nope=False)

    def test_generate(self):

        statement = LIMITED("people", SELECT=test_clause.FIELDS("*"), LIMIT=5)

        statement.generate()
        self.assertEqual(statement.sql, "LIMITED `people` * LIMIT %s")
        self.assertEqual(statement.args, [5])

        statement.LIMIT(10)

        self.assertRaisesRegex(relations_sql.SQLError, "LIMIT can only be total", statement.generate)


class UPDATE(relations_sql.UPDATE):

    NAME = "UPDATE"

    CLAUSES = collections.OrderedDict([
        ("OPTIONS", test_clause.OPTIONS),
        ("TABLE", test_expression.TABLE),
        ("SET", test_clause.SET),
        ("WHERE", test_clause.WHERE),
        ("ORDER_BY", test_clause.ORDER_BY),
        ("LIMIT", test_clause.LIMIT)
    ])

class TestUPDATE(unittest.TestCase):

    maxDiff = None

    def test_generate(self):

        statement = UPDATE("people").SET(stuff="things").WHERE(things="stuff")
        statement.OPTIONS("FAST").ORDER_BY("yin", yang=DESC).LIMIT(5)

        statement.generate()
        self.assertEqual(statement.sql, "UPDATE FAST `people` SET `stuff`=%s WHERE `things`=%s ORDER BY `yin`,`yang` DESC LIMIT %s")
        self.assertEqual(statement.args, ["things", "stuff", 5])

        statement.LIMIT(10)

        self.assertRaisesRegex(relations_sql.SQLError, "LIMIT can only be total", statement.generate)


class DELETE(relations_sql.DELETE):

    NAME = "DELETE"

    CLAUSES = collections.OrderedDict([
        ("OPTIONS", test_clause.OPTIONS),
        ("TABLE", test_expression.TABLE),
        ("WHERE", test_clause.WHERE),
        ("ORDER_BY", test_clause.ORDER_BY),
        ("LIMIT", test_clause.LIMIT)
    ])

class TestDELETE(unittest.TestCase):

    maxDiff = None

    def test_generate(self):

        statement = DELETE("people").WHERE(things="stuff")
        statement.OPTIONS("FAST").ORDER_BY("yin", yang=DESC).LIMIT(5)

        statement.generate()
        self.assertEqual(statement.sql, "DELETE FAST FROM `people` WHERE `things`=%s ORDER BY `yin`,`yang` DESC LIMIT %s")
        self.assertEqual(statement.args, ["stuff", 5])

        statement.LIMIT(10)

        self.assertRaisesRegex(relations_sql.SQLError, "LIMIT can only be total", statement.generate)
