import os
import sqlite3

import aiosqlite


class DatabaseCommands:

    def __init__(self, table: str):
        self.table = table

    async def add(self, **kwargs):
        raw_values = (f"'{value}'" for value in kwargs.values())
        keys, values = ', '.join(kwargs.keys()), ', '.join(raw_values)
        async with aiosqlite.connect("db.db", check_same_thread=False) as conn:
            conn.row_factory = self.__dict_factory
            await conn.execute(f"INSERT INTO {self.table} ({keys}) VALUES ({values})")
            await conn.commit()
            params = [f"{key}='{value}'" for key, value in kwargs.items()]
            cursor = await conn.execute(f"SELECT * FROM {self.table} WHERE {'AND '.join(params)}")
            h = await cursor.fetchone()
            return h

    async def update(self, id_value: int, **kwargs):
        async with aiosqlite.connect("db.db", check_same_thread=False) as conn:
            params = ",".join(f"{key}='{value}'" for key, value in kwargs.items())
            await conn.execute(f"UPDATE {self.table} SET {params} WHERE id={id_value}")
            await conn.commit()

    async def get(self, id_value: int = None, get_all: bool = False) -> sqlite3.Row | list:
        if any([id_value, get_all]):
            async with aiosqlite.connect('db.db', check_same_thread=False) as conn:
                conn.row_factory = self.__dict_factory
                cursor = await conn.execute(f"SELECT * FROM {self.table}"
                                            f" {'WHERE id=' if not get_all else ''}{id_value if not get_all else ''}")
                return await cursor.fetchone() if not get_all else await cursor.fetchall()
        else:
            raise ValueError

    async def delete(self, id_value: int):
        async with aiosqlite.connect("db.db", check_same_thread=False) as conn:
            await conn.execute(f"DELETE FROM {self.table} WHERE id={id_value}")
            await conn.commit()

    @classmethod
    async def custom_sql(cls, sql: str, to_dict=True):
        async with aiosqlite.connect("db.db", check_same_thread=False) as conn:
            conn.row_factory = cls.__dict_factory if to_dict else None
            cursor = await conn.execute(sql)
            h = await cursor.fetchall()
            await conn.commit()
            return h

    @classmethod
    async def create_database(cls):
        if os.path.exists("db.db"):
            return
        sql_requests = ["create table notifications"
                        "(id             integer "
                        "constraint notifications_pk "
                        "primary key autoincrement,"
                        "user_id        integer,"
                        "desc           text,"
                        "date_complete"
                        " text,"
                        "title          text,"
                        "is_on          integer default 1,"
                        "date_set       text);",

                        "create table users"
                        "(id         integer "
                        "constraint users_pk "
                        "primary key,"
                        "username   text,"
                        "registered real,"
                        "lang       text default 'en',"
                        "time_zone  text);",
                        "create table time_zones"
                        "(id             integer "
                        "constraint time_zone_pk "
                        "primary key autoincrement,"
                        "time_zone       text);"
                        ]
        async with aiosqlite.connect("db.db", check_same_thread=False) as conn:
            for sql in sql_requests:
                await conn.execute(sql)
            await conn.commit()

    @staticmethod
    def __dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

