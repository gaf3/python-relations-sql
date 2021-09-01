import unittest
import unittest.mock

import test_expression
import test_criterion
import test_clause

import collections

import relations_sql


class QUERY(relations_sql.QUERY):

    NAME = "QUERY"

    CLAUSES = collections.OrderedDict([
        ("SELECT", test_clause.FIELDS),
        ("FROM", test_clause.FROM)
    ])

class TestQUERY(unittest.TestCase):

    maxDiff = None

    def test___init__(self):

        query = QUERY()

        self.assertEqual(query.SELECT.expressions, [])
        self.assertEqual(query.FROM.expressions, [])

        query = QUERY(SELECT="people.stuff", FROM=test_clause.FROM("things"))

        self.assertEqual(query.SELECT.expressions[0].table.name, "people")
        self.assertEqual(query.SELECT.expressions[0].name, "stuff")
        self.assertEqual(query.FROM.expressions[0].name, "things")

        self.assertRaisesRegex(TypeError, "'nope' is an invalid keyword argument for QUERY", QUERY, nope=False)

    def test___getattr__(self):

        model = unittest.mock.MagicMock()
        query = QUERY(SELECT="people.stuff", FROM="things").bind(model)

        query.retrieve(False)

        model.retrieve.assert_called_once_with(False)

        def nope():

            query.nope

        self.assertRaisesRegex(AttributeError, "object has no attribute", nope)

    def test___len__(self):

        query = QUERY(SELECT="people.stuff", FROM="things")

        self.assertEqual(len(query), 2)

    def test_check(self):

        query = QUERY(SELECT="people.stuff", FROM="things")

        query.check({})
        self.assertEqual(query.clauses, {})

        self.assertRaisesRegex(TypeError, "'nope' is an invalid keyword argument for QUERY", QUERY, nope=False)

    def test_bind(self):

        model = unittest.mock.MagicMock()
        query = QUERY(SELECT="people.stuff", FROM="things").bind(model)

        self.assertEqual(query.model, model)

    def test_generate(self):

        query = QUERY(SELECT="people.stuff", FROM="things")

        query.generate()
        self.assertEqual(query.sql, "QUERY `people`.`stuff` FROM `things`")
        self.assertEqual(query.args, [])


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

        query = SELECT("*").FROM("people").WHERE(stuff__gt="things")

        self.assertEqual(query.FIELDS.expressions[0].name, "*")
        self.assertEqual(query.FROM.expressions[0].name, "people")
        self.assertIsInstance(query.WHERE.expressions[0], test_criterion.GT)
        self.assertEqual(query.WHERE.expressions[0].left.name, "stuff")
        self.assertEqual(query.WHERE.expressions[0].right.value, "things")

    def test_generate(self):

        query = SELECT("*").OPTIONS("FAST").FROM("people").WHERE(stuff__gt="things")

        query.generate()
        self.assertEqual(query.sql, "SELECT FAST * FROM `people` WHERE `stuff`>%s")
        self.assertEqual(query.args, ["things"])

        query = SELECT(
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

        query.generate()
        self.assertEqual(query.sql,
            "SELECT * FROM (SELECT `a`.`b`.`c` FROM `d`.`e`) "
            "AS `people` WHERE `stuff` IN "
            "(SELECT `f` FROM `g` WHERE `things`>%s>JSON(%s))"
        )
        self.assertEqual(query.args, ['$."a"[0][-1]."2"."-3"', '5'])

        query.GROUP_BY("fee", "fie").HAVING(foe="fum").ORDER_BY("yin", yang=DESC).LIMIT(1, 2)

        query.generate()
        self.assertEqual(query.sql,
            "SELECT * FROM (SELECT `a`.`b`.`c` FROM `d`.`e`) "
            "AS `people` WHERE `stuff` IN "
            "(SELECT `f` FROM `g` WHERE `things`>%s>JSON(%s)) "
            "GROUP BY `fee`,`fie` HAVING `foe`=%s "
            "ORDER BY `yin`,`yang` DESC LIMIT %s,%s"
        )
        self.assertEqual(query.args, ['$."a"[0][-1]."2"."-3"', '5', 'fum', 1, 2])


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

        query = INSERT("people.stuff", "things", SELECT="*")

        self.assertEqual(query.TABLE.name, "stuff")
        self.assertEqual(query.TABLE.schema.name, "people")
        self.assertEqual(query.FIELDS.expressions[0].name, "things")
        self.assertEqual(query.SELECT.FIELDS.expressions[0].name, "*")

        query = INSERT("people.stuff", FIELDS=["things"], SELECT=SELECT("stuff").FROM("things"))

        self.assertEqual(query.TABLE.name, "stuff")
        self.assertEqual(query.TABLE.schema.name, "people")
        self.assertEqual(query.FIELDS.expressions[0].name, "things")

        self.assertRaisesRegex(TypeError, "'nope' is an invalid keyword argument for INSERT", INSERT, "table", nope=False)

    def test_field(self):

        query = INSERT("people.stuff")

        query.field(["things"])
        self.assertEqual(query.FIELDS.expressions[0].name, "things")

        query.field(["thingies"])
        self.assertEqual(query.FIELDS.expressions[0].name, "things")

    def test_generate(self):

        query = INSERT("people").VALUES(stuff=1, things=2).VALUES(3, 4)

        query.generate()
        self.assertEqual(query.sql,"INSERT INTO `people` (`stuff`,`things`) VALUES (%s,%s),(%s,%s)")
        self.assertEqual(query.args, [1, 2, 3, 4])

        query = INSERT("people").OPTIONS("FAST")
        query.SELECT("stuff").FROM("things")

        query.generate()
        self.assertEqual(query.sql,"INSERT FAST INTO `people` SELECT `stuff` FROM `things`")
        self.assertEqual(query.args, [])

        query = INSERT("people").VALUES(stuff=1, things=2).VALUES(3, 4)
        query.SELECT("stuff").FROM("things")

        self.assertRaisesRegex(relations_sql.SQLError, "set VALUES or SELECT but not both", query.generate)


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

        query = LIMITED("people", SELECT="*")

        self.assertEqual(query.SELECT.expressions[0].name, "*")
        self.assertEqual(query.TABLE.name, "people")

        query = LIMITED("people", SELECT=test_clause.FIELDS("*"))

        self.assertEqual(query.SELECT.expressions[0].name, "*")
        self.assertEqual(query.TABLE.name, "people")

        query = LIMITED("people")

        self.assertEqual(query.SELECT.expressions, [])
        self.assertEqual(query.TABLE.name, "people")

        self.assertRaisesRegex(TypeError, "'nope' is an invalid keyword argument for INSERT", INSERT, "table", nope=False)

    def test_generate(self):

        query = LIMITED("people", SELECT=test_clause.FIELDS("*"), LIMIT=5)

        query.generate()
        self.assertEqual(query.sql, "LIMITED `people` * LIMIT %s")
        self.assertEqual(query.args, [5])

        query.LIMIT(10)

        self.assertRaisesRegex(relations_sql.SQLError, "LIMIT can only be total", query.generate)


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

        query = UPDATE("people").SET(stuff="things").WHERE(things="stuff")
        query.OPTIONS("FAST").ORDER_BY("yin", yang=DESC).LIMIT(5)

        query.generate()
        self.assertEqual(query.sql, "UPDATE FAST `people` SET `stuff`=%s WHERE `things`=%s ORDER BY `yin`,`yang` DESC LIMIT %s")
        self.assertEqual(query.args, ["things", "stuff", 5])

        query.LIMIT(10)

        self.assertRaisesRegex(relations_sql.SQLError, "LIMIT can only be total", query.generate)


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

        query = DELETE("people").WHERE(things="stuff")
        query.OPTIONS("FAST").ORDER_BY("yin", yang=DESC).LIMIT(5)

        query.generate()
        self.assertEqual(query.sql, "DELETE FAST FROM `people` WHERE `things`=%s ORDER BY `yin`,`yang` DESC LIMIT %s")
        self.assertEqual(query.args, ["stuff", 5])

        query.LIMIT(10)

        self.assertRaisesRegex(relations_sql.SQLError, "LIMIT can only be total", query.generate)
