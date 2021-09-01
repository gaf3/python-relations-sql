# python-relations-sql

Module for interacting with Relations and SQL

This is an abstract library that'll be used to create libraries for pymysql, psycopg2, sqlite3, etc.

But here's some of the main unittests so you get the general idea.

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
