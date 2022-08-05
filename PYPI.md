# relations-sql

Module for interacting with Relations and SQL

This is an abstract library used by relations-mysql, relations-postgresql, relations-sqlite, etc. to generate queries specific to those databases.

But folks may find it useful for their usages. So here's some of the main unittests so you get the general idea.

I'll probably switch this to ANSI SQL? I dunno. Not sure how useful that'll be.

# import

All the classes are capitalized to prevent collisions with reserved keywords. Plus it looks like actual SQL. So you can do a full import without worries.

```python
from relations_sql import *
```

# select

```python
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
    "(SELECT `f` FROM `g` WHERE `things`#>>%s>JSON(%s))"
)
self.assertEqual(query.args, ['$."a"[0][-1]."2"."-3"', '5'])

query.GROUP_BY("fee", "fie").HAVING(foe="fum").ORDER_BY("yin", yang=DESC).LIMIT(1, 2)

query.generate()
self.assertEqual(query.sql,
    "SELECT * FROM (SELECT `a`.`b`.`c` FROM `d`.`e`) "
    "AS `people` WHERE `stuff` IN "
    "(SELECT `f` FROM `g` WHERE `things`#>>%s>JSON(%s)) "
    "GROUP BY `fee`,`fie` HAVING `foe`=%s "
    "ORDER BY `yin`,`yang` DESC LIMIT %s,%s"
)
self.assertEqual(query.args, ['$."a"[0][-1]."2"."-3"', '5', 'fum', 1, 2])
```

# insert

```python
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
```

# update

```python
query = UPDATE("people").SET(stuff="things").WHERE(things="stuff")
query.OPTIONS("FAST").ORDER_BY("yin", yang=DESC).LIMIT(5)

query.generate()
self.assertEqual(query.sql, "UPDATE FAST `people` SET `stuff`=%s WHERE `things`=%s ORDER BY `yin`,`yang` DESC LIMIT %s")
self.assertEqual(query.args, ["things", "stuff", 5])

query.LIMIT(10)

self.assertRaisesRegex(relations_sql.SQLError, "LIMIT can only be total", query.generate)
```

# delete

```python
query = DELETE("people").WHERE(things="stuff")
query.OPTIONS("FAST").ORDER_BY("yin", yang=DESC).LIMIT(5)

query.generate()
self.assertEqual(query.sql, "DELETE FAST FROM `people` WHERE `things`=%s ORDER BY `yin`,`yang` DESC LIMIT %s")
self.assertEqual(query.args, ["stuff", 5])

query.LIMIT(10)

self.assertRaisesRegex(relations_sql.SQLError, "LIMIT can only be total", query.generate)
```

# inherit

The unittest demonstrate how to abstract through inheritance. Classes know which other classes they'll need through class attributes.

The unittests are where the backticks escaping comes from. It's not a default or anything.

In `test_clause.py`

```python
class OPTIONS(relations_sql.OPTIONS):

    pass


class FIELDS(relations_sql.FIELDS):

    ARGS = test_expression.FIELD
    KWARG = test_expression.FIELD
    KWARGS = test_expression.AS
```

In `test_query.py`

```python
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


class INSERT(relations_sql.INSERT):

    CLAUSES = collections.OrderedDict([
        ("OPTIONS", test_clause.OPTIONS),
        ("TABLE", test_expression.TABLE),
        ("FIELDS", test_expression.NAMES),
        ("VALUES", test_clause.VALUES),
        ("SELECT", SELECT)
    ])


class UPDATE(relations_sql.UPDATE):

    CLAUSES = collections.OrderedDict([
        ("OPTIONS", test_clause.OPTIONS),
        ("TABLE", test_expression.TABLE),
        ("SET", test_clause.SET),
        ("WHERE", test_clause.WHERE),
        ("ORDER_BY", test_clause.ORDER_BY),
        ("LIMIT", test_clause.LIMIT)
    ])


class DELETE(relations_sql.DELETE):

    CLAUSES = collections.OrderedDict([
        ("OPTIONS", test_clause.OPTIONS),
        ("TABLE", test_expression.TABLE),
        ("WHERE", test_clause.WHERE),
        ("ORDER_BY", test_clause.ORDER_BY),
        ("LIMIT", test_clause.LIMIT)
    ])
```

In the case of query classes, the OrderedDict's there also specific the order in which clauses are generated and appended. So it's pretty easy to extend.
