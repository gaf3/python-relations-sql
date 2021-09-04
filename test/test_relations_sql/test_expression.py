import unittest
import unittest.mock

import test_sql

import relations_sql

class UNQUOTED(relations_sql.EXPRESSION):
    pass

class QUOTED(test_sql.SQL, relations_sql.EXPRESSION):
    pass

class TestEXPRESSION(unittest.TestCase):

    maxDiff = None

    def test_quote(self):

        expression = UNQUOTED()
        self.assertEqual(expression.quote("unit"), "unit")

        expression = QUOTED()
        self.assertEqual(expression.quote("test"), "`test`")

    def test_express(self):

        expression = QUOTED("test")

        expression.express(None, None)

        sql = []
        expression.args = []
        expressions = [relations_sql.SQL("fee", ["fie"]), relations_sql.SQL("foe", ["fum"])]

        expression.express(expressions, sql)
        self.assertEqual(sql, ["fee", "foe"])
        self.assertEqual(expression.args, ["fie", "fum"])


class VALUE(test_sql.SQL, relations_sql.VALUE):
    pass

class TestVALUE(unittest.TestCase):

    maxDiff = None

    def test___init__(self):

        expression = VALUE("unit")
        self.assertEqual(expression.value, "unit")
        self.assertFalse(expression.jsonify)

        expression = VALUE("test", jsonify=True)
        self.assertEqual(expression.value, "test")
        self.assertTrue(expression.jsonify)

        expression = VALUE({"a": 1})
        self.assertEqual(expression.value, {"a": 1})
        self.assertTrue(expression.jsonify)

    def test___len__(self):

        expression = VALUE("unit")
        self.assertEqual(len(expression), 1)

    def test_generate(self):

        expression = VALUE("unit")
        expression.generate()
        self.assertEqual(expression.sql, "%s")
        self.assertEqual(expression.args, ["unit"])

        expression = VALUE("test", jsonify=True)
        expression.generate()
        self.assertEqual(expression.sql, "JSON(%s)")
        self.assertEqual(expression.args, ['"test"'])

        expression = VALUE({"a": 1})
        expression.generate()
        self.assertEqual(expression.sql, "JSON(%s)")
        self.assertEqual(expression.args, ['{"a": 1}'])


class NOT(test_sql.SQL, relations_sql.NOT):

    VALUE = VALUE

class TestNOT(unittest.TestCase):

    maxDiff = None

    def test___init__(self):

        expression = NOT("unit")
        self.assertIsInstance(expression.expression, VALUE)
        self.assertEqual(expression.expression.value, "unit")

        expression = NOT(relations_sql.SQL("test"))
        self.assertEqual(expression.expression.sql, "test")

    def test_generate(self):

        expression = NOT("unit")
        expression.generate()
        self.assertEqual(expression.sql, "NOT %s")
        self.assertEqual(expression.args, ["unit"])

        expression = NOT(relations_sql.SQL("test"))
        expression.generate()
        self.assertEqual(expression.sql, "NOT test")
        self.assertEqual(expression.args, [])


class LIST(test_sql.SQL, relations_sql.LIST):

    ARG = VALUE

class TestLIST(unittest.TestCase):

    maxDiff = None

    def test___init__(self):

        expression = LIST(["unit", "test"])
        self.assertIsInstance(expression.expressions[0], VALUE)
        self.assertEqual(expression.expressions[0].value, "unit")
        self.assertFalse(expression.expressions[0].jsonify)
        self.assertIsInstance(expression.expressions[1], VALUE)
        self.assertEqual(expression.expressions[1].value, "test")
        self.assertFalse(expression.expressions[1].jsonify)

        expression = LIST(["unit", "test"], jsonify=True)
        self.assertIsInstance(expression.expressions[0], VALUE)
        self.assertEqual(expression.expressions[0].value, "unit")
        self.assertTrue(expression.expressions[0].jsonify)
        self.assertIsInstance(expression.expressions[1], VALUE)
        self.assertEqual(expression.expressions[1].value, "test")
        self.assertTrue(expression.expressions[1].jsonify)

        expression = LIST([{"a": 1}, VALUE({"b": 2})])
        self.assertIsInstance(expression.expressions[0], VALUE)
        self.assertEqual(expression.expressions[0].value, {"a": 1})
        self.assertTrue(expression.expressions[0].jsonify)
        self.assertIsInstance(expression.expressions[1], VALUE)
        self.assertEqual(expression.expressions[1].value, {"b": 2})
        self.assertTrue(expression.expressions[1].jsonify)

    def test___len__(self):

        expression = LIST([])
        self.assertEqual(len(expression), 0)

        expression = LIST(["unit", "test"])
        self.assertEqual(len(expression), 2)

    def test_generate(self):

        expression = LIST(["unit", "test"])
        expression.generate()
        self.assertEqual(expression.sql, "%s,%s")
        self.assertEqual(expression.args, ["unit", "test"])

        expression = LIST(["unit", "test"], jsonify=True)
        expression.generate()
        self.assertEqual(expression.sql, "JSON(%s),JSON(%s)")
        self.assertEqual(expression.args, ['"unit"', '"test"'])

        expression = LIST([{"a": 1}, {"b": 2}])
        expression.generate()
        self.assertEqual(expression.sql, "JSON(%s),JSON(%s)")
        self.assertEqual(expression.args, ['{"a": 1}', '{"b": 2}'])


class NAME(test_sql.SQL, relations_sql.NAME):
    pass

class TestNAME(unittest.TestCase):

    maxDiff = None

    def test___init__(self):

        expression = NAME("people")
        self.assertEqual(expression.name, "people")

    def test___call__(self):

        expression = NAME("")
        expression("people")
        self.assertEqual(expression.name, "people")

    def test_set(self):

        expression = NAME("")
        expression.set("people")
        self.assertEqual(expression.name, "people")

    def test___len__(self):

        expression = NAME("people")
        self.assertEqual(len(expression), 1)

    def test_generate(self):

        expression = NAME("people")
        expression.generate()
        self.assertEqual(expression.sql, "`people`")
        self.assertEqual(expression.args, [])


class SCHEMA(test_sql.SQL, relations_sql.SCHEMA):
    pass

class TestSCHEMA(unittest.TestCase):

    maxDiff = None

    def test___init__(self):

        expression = SCHEMA("people")
        self.assertEqual(expression.name, "people")

    def test___call__(self):

        expression = SCHEMA("")
        expression("people")
        self.assertEqual(expression.name, "people")

    def test_set(self):

        expression = SCHEMA("")
        expression.set("people")
        self.assertEqual(expression.name, "people")

    def test_generate(self):

        expression = SCHEMA("people")
        expression.generate()
        self.assertEqual(expression.sql, "`people`")
        self.assertEqual(expression.args, [])


class TABLE(test_sql.SQL, relations_sql.TABLE):

    SCHEMA = SCHEMA

class TestTABLE(unittest.TestCase):

    maxDiff = None

    def test___init__(self):

        expression = TABLE("stuff")
        self.assertEqual(expression.name, "stuff")
        self.assertIsNone(expression.schema)

        expression = TABLE("people.stuff", prefix="things")
        self.assertEqual(expression.name, "stuff")
        self.assertEqual(expression.prefix, "things")
        self.assertIsInstance(expression.schema, SCHEMA)
        self.assertEqual(expression.schema.name, "people")

        expression = TABLE("stuff", "people")
        self.assertEqual(expression.name, "stuff")
        self.assertIsInstance(expression.schema, SCHEMA)
        self.assertEqual(expression.schema.name, "people")

        schema = relations_sql.SQL()
        expression = TABLE("stuff", schema=schema)
        self.assertEqual(expression.name, "stuff")
        self.assertEqual(expression.schema, schema)

    def test___call__(self):

        expression = TABLE('')
        expression("stuff")
        self.assertEqual(expression.name, "stuff")
        self.assertIsNone(expression.schema)

        expression("people.stuff", prefix="things")
        self.assertEqual(expression.name, "stuff")
        self.assertEqual(expression.prefix, "things")
        self.assertIsInstance(expression.schema, SCHEMA)
        self.assertEqual(expression.schema.name, "people")

        expression("stuff", "people")
        self.assertEqual(expression.name, "stuff")
        self.assertIsInstance(expression.schema, SCHEMA)
        self.assertEqual(expression.schema.name, "people")

        schema = relations_sql.SQL()
        expression("stuff", schema=schema)
        self.assertEqual(expression.name, "stuff")
        self.assertEqual(expression.schema, schema)

    def test_set(self):

        expression = TABLE('')
        expression.set("stuff")
        self.assertEqual(expression.name, "stuff")
        self.assertIsNone(expression.schema)

        expression.set("people.stuff", prefix="things")
        self.assertEqual(expression.name, "stuff")
        self.assertEqual(expression.prefix, "things")
        self.assertIsInstance(expression.schema, SCHEMA)
        self.assertEqual(expression.schema.name, "people")

        expression.set("stuff", "people")
        self.assertEqual(expression.name, "stuff")
        self.assertIsInstance(expression.schema, SCHEMA)
        self.assertEqual(expression.schema.name, "people")

        schema = relations_sql.SQL()
        expression.set("stuff", schema=schema)
        self.assertEqual(expression.name, "stuff")
        self.assertEqual(expression.schema, schema)

    def test_generate(self):

        expression = TABLE("people.stuff", prefix="things")
        expression.generate()
        self.assertEqual(expression.sql, "things `people`.`stuff`")
        self.assertEqual(expression.args, [])

        schema = relations_sql.SQL("unit", ["test"])
        expression = TABLE("stuff", schema=schema)
        expression.generate()
        self.assertEqual(expression.sql, "unit.`stuff`")
        self.assertEqual(expression.args, ["test"])


class FIELD(test_sql.SQL, relations_sql.FIELD):

    TABLE = TABLE

    def walk(self):

        places = []

        for place in self.path:
            if isinstance(place, int):
                places.append(f"[{int(place)}]")
            else:
                places.append(f'."{place}"')

        return f"${''.join(places)}"

class TestFIELD(unittest.TestCase):

    maxDiff = None

    def test___init__(self):

        expression = FIELD("people.stuff.things", jsonify=True)

        self.assertEqual(expression.name, "things")
        self.assertIsInstance(expression.table, TABLE)
        self.assertEqual(expression.table.name, "stuff")
        self.assertIsInstance(expression.table.schema, SCHEMA)
        self.assertEqual(expression.table.schema.name, "people")
        self.assertEqual(expression.path, [])
        self.assertTrue(expression.jsonify)

        table = relations_sql.SQL("test", ["unit"])

        expression = FIELD("people.stuff.things__a__0___1____2_____3", table=table)
        self.assertEqual(expression.name, "things")
        self.assertEqual(expression.table, table)
        self.assertEqual(expression.path, ["a", 0, -1, "2", "-3"])
        self.assertFalse(expression.jsonify)

        schema = relations_sql.SQL("unit", ["test"])

        expression = FIELD("people.stuff.things__a__0___1____2_____3", schema=schema, extracted=True)
        self.assertEqual(expression.name, "things__a__0___1____2_____3")
        self.assertEqual(expression.table.name, "stuff")
        self.assertEqual(expression.table.schema, schema)
        self.assertEqual(expression.path, [])
        self.assertFalse(expression.jsonify)

    def test___call__(self):

        expression = FIELD('a')
        expression("people.stuff.things", jsonify=True)

        self.assertEqual(expression.name, "things")
        self.assertIsInstance(expression.table, TABLE)
        self.assertEqual(expression.table.name, "stuff")
        self.assertIsInstance(expression.table.schema, SCHEMA)
        self.assertEqual(expression.table.schema.name, "people")
        self.assertEqual(expression.path, [])
        self.assertTrue(expression.jsonify)

        table = relations_sql.SQL("test", ["unit"])

        expression("people.stuff.things__a__0___1____2_____3", table=table)
        self.assertEqual(expression.name, "things")
        self.assertEqual(expression.table, table)
        self.assertEqual(expression.path, ["a", 0, -1, "2", "-3"])
        self.assertFalse(expression.jsonify)

        schema = relations_sql.SQL("unit", ["test"])

        expression("people.stuff.things__a__0___1____2_____3", schema=schema, extracted=True)
        self.assertEqual(expression.name, "things__a__0___1____2_____3")
        self.assertEqual(expression.table.name, "stuff")
        self.assertEqual(expression.table.schema, schema)
        self.assertEqual(expression.path, [])
        self.assertFalse(expression.jsonify)

    def test___call__(self):

        expression = FIELD('a')
        expression.set("people.stuff.things", jsonify=True)

        self.assertEqual(expression.name, "things")
        self.assertIsInstance(expression.table, TABLE)
        self.assertEqual(expression.table.name, "stuff")
        self.assertIsInstance(expression.table.schema, SCHEMA)
        self.assertEqual(expression.table.schema.name, "people")
        self.assertEqual(expression.path, [])
        self.assertTrue(expression.jsonify)

        table = relations_sql.SQL("test", ["unit"])

        expression.set("people.stuff.things__a__0___1____2_____3", table=table)
        self.assertEqual(expression.name, "things")
        self.assertEqual(expression.table, table)
        self.assertEqual(expression.path, ["a", 0, -1, "2", "-3"])
        self.assertFalse(expression.jsonify)

        schema = relations_sql.SQL("unit", ["test"])

        expression.set("people.stuff.things__a__0___1____2_____3", schema=schema, extracted=True)
        self.assertEqual(expression.name, "things__a__0___1____2_____3")
        self.assertEqual(expression.table.name, "stuff")
        self.assertEqual(expression.table.schema, schema)
        self.assertEqual(expression.path, [])
        self.assertFalse(expression.jsonify)

    def test_split(self):

        self.assertEqual(FIELD.split("people.stuff.things"), ("people.stuff.things", []))

        self.assertEqual(FIELD.split("people_stuff__a__0___1____2_____3"), ("people_stuff", ["a", 0, -1, "2", "-3"]))

    def test_field(self):

        expression = FIELD("people.stuff.things")
        expression.args = []

        self.assertEqual(expression.field(), "`people`.`stuff`.`things`")

    def test_generate(self):

        expression = FIELD("*")
        expression.generate()
        self.assertEqual(expression.sql, "*")
        self.assertEqual(expression.args, [])

        expression = FIELD("people.stuff.things", jsonify=True)
        expression.generate()
        self.assertEqual(expression.sql, "JSON(`people`.`stuff`.`things`)")
        self.assertEqual(expression.args, [])

        table = relations_sql.SQL("test", ["unit"])

        expression = FIELD("people.stuff.things__a__0___1____2_____3", table=table)
        expression.generate()
        self.assertEqual(expression.sql, "test.`things`#>>%s")
        self.assertEqual(expression.args, ["unit", '$."a"[0][-1]."2"."-3"'])

        schema = relations_sql.SQL("unit", ["test"])

        expression = FIELD("people.stuff.things__a__0___1____2_____3", schema=schema)
        expression.generate()
        self.assertEqual(expression.sql, "unit.`stuff`.`things`#>>%s")
        self.assertEqual(expression.args, ["test", '$."a"[0][-1]."2"."-3"'])


class NAMES(test_sql.SQL, relations_sql.NAMES):

    ARG = NAME

class TestNAMES(unittest.TestCase):

    maxDiff = None

    def test___init__(self):

        expression = NAMES(["unit", relations_sql.SQL("test")])
        self.assertIsInstance(expression.expressions[0], NAME)
        self.assertEqual(expression.expressions[0].name, "unit")
        self.assertIsInstance(expression.expressions[1], relations_sql.SQL)
        self.assertEqual(expression.expressions[1].sql, "test")

    def test_generate(self):

        expression = NAMES(["unit", relations_sql.SQL("test")])
        expression.generate()
        self.assertEqual(expression.sql, "`unit`,test")
        self.assertEqual(expression.args, [])


class AS(test_sql.SQL, relations_sql.AS):

    NAME = NAME

class TestAS(unittest.TestCase):

    maxDiff = None

    def test___init__(self):

        field = relations_sql.SQL("test", ["unit"])

        expression = AS("people", field)
        self.assertIsInstance(expression.label, NAME)
        self.assertEqual(expression.label.name, "people")
        self.assertEqual(expression.expression, field)

        label = relations_sql.SQL("unit", ["test"])

        expression = AS(label, field)
        self.assertEqual(expression.label, label)
        self.assertEqual(expression.expression, field)

    def test___len__(self):

        field = relations_sql.SQL("test", ["unit"])

        expression = AS("people", field)
        self.assertEqual(len(expression), 2)

    def test_generate(self):

        field = relations_sql.SQL("test", ["unit"])

        expression = AS("people", field)
        expression.generate()
        self.assertEqual(expression.sql, "test AS `people`")
        self.assertEqual(expression.args, ["unit"])

        label = relations_sql.SQL("unit", ["test"])

        expression = AS(label, field)
        expression.generate()
        self.assertEqual(expression.sql, "test AS unit")
        self.assertEqual(expression.args, ["unit", "test"])

ASC = relations_sql.ASC
DESC = relations_sql.DESC

class ORDER(test_sql.SQL, relations_sql.ORDER):

    EXPRESSION = FIELD

class TestORDER(unittest.TestCase):

    maxDiff = None

    def test___init__(self):

        expression = ORDER("people")
        self.assertIsInstance(expression.expression, FIELD)
        self.assertEqual(expression.expression.name, "people")
        self.assertIsNone(expression.order)

        expression = ORDER("people", ASC)
        self.assertIsInstance(expression.expression, FIELD)
        self.assertEqual(expression.expression.name, "people")
        self.assertEqual(expression.order, ASC)

        expression = ORDER(people=DESC)
        self.assertIsInstance(expression.expression, FIELD)
        self.assertEqual(expression.expression.name, "people")
        self.assertEqual(expression.order, DESC)

        field = relations_sql.SQL("test", ["unit"])

        expression = ORDER(field)
        self.assertEqual(expression.expression, field)
        self.assertIsNone(expression.order)

        self.assertRaisesRegex(relations_sql.SQLError, "need single pair", ORDER, a=1, b=2)
        self.assertRaisesRegex(relations_sql.SQLError, "must be in", ORDER, order="nope")

    def test___len__(self):

        expression = ORDER("people")
        self.assertEqual(len(expression), 1)

    def test_generate(self):

        expression = ORDER("people")
        expression.generate()
        self.assertEqual(expression.sql, "`people`")
        self.assertEqual(expression.args, [])

        expression = ORDER("people", ASC)
        expression.generate()
        self.assertEqual(expression.sql, "`people` ASC")
        self.assertEqual(expression.args, [])

        expression = ORDER(people=DESC)
        expression.generate()
        self.assertEqual(expression.sql, "`people` DESC")
        self.assertEqual(expression.args, [])

        field = relations_sql.SQL("test", ["unit"])

        expression = ORDER(field)
        expression.generate()
        self.assertEqual(expression.sql, "test")
        self.assertEqual(expression.args, ["unit"])

        field = relations_sql.SQL("", [])

        expression = ORDER(field)
        self.assertFalse(expression.generate())


class ASSIGN(test_sql.SQL, relations_sql.ASSIGN):

    FIELD = NAME
    EXPRESSION = VALUE

class TestASSIGN(unittest.TestCase):

    maxDiff = None

    def test___init__(self):

        expression = ASSIGN("people", "stuff")
        self.assertIsInstance(expression.field, NAME)
        self.assertIsInstance(expression.expression, VALUE)
        self.assertEqual(expression.field.name, "people")
        self.assertEqual(expression.expression.value, "stuff")

        field = relations_sql.SQL("unit", ["test"])
        value = relations_sql.SQL("test", ["unit"])

        expression = ASSIGN(field, value)
        self.assertEqual(expression.field, field)
        self.assertEqual(expression.expression, value)

    def test___len__(self):

        expression = ASSIGN("people", "stuff")
        self.assertEqual(len(expression), 2)

    def test_generate(self):

        expression = ASSIGN("people", "stuff")
        expression.generate()
        self.assertEqual(expression.sql, "`people`=%s")
        self.assertEqual(expression.args, ["stuff"])

        field = relations_sql.SQL("unit", ["test"])
        value = relations_sql.SQL("test", ["unit"])

        expression = ASSIGN(field, value)
        expression.generate()
        self.assertEqual(expression.sql, "unit=test")
        self.assertEqual(expression.args, ["test", "unit"])
