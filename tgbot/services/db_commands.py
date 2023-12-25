
import asyncpg

from asyncpg import Pool


class DatabaseCommands:

    _pool: Pool = None  # Общий пул

    def __init__(self, table: str):
        self.table = table

    @classmethod
    async def connect(cls, user, password, database, host):
        cls._pool = await asyncpg.create_pool(user=user, password=password,
                                              database=database, host=host)

    @classmethod
    async def close(cls):
        if cls._pool:
            await cls._pool.close()

    async def execute_query(self, query, *args):
        async with self._pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetch_query(self, query, *args, return_one_record_list=False):
        async with self._pool.acquire() as conn:
            result = await conn.fetch(query, *args)
            if return_one_record_list:
                return result
            return result[0] if result and len(result) == 1 else result

    async def add(self, **kwargs) -> asyncpg.Record:
        keys, values = zip(*kwargs.items())
        query = f"INSERT INTO {self.table} ({', '.join(keys)}) VALUES " \
                f"({', '.join(['$'+str(i) for i in range(1, len(values) + 1)])}) RETURNING *"
        return await self.fetch_query(query, *values)

    async def update(self, id_value: int, **kwargs) -> None:
        set_values = ', '.join([f"{key} = ${i}" for i, (key, value) in enumerate(kwargs.items(), start=2)])
        query = f"UPDATE {self.table} SET {set_values} WHERE id = $1"
        await self.execute_query(query, id_value, *kwargs.values())

    async def get(self, id_value: int = None, get_all: bool = False, **custom_params) -> asyncpg.Record | list:
        if get_all:
            return await self.fetch_query(f"SELECT * FROM {self.table}", return_one_record_list=True)
        elif custom_params:
            conditions = " AND ".join([f"{key} = ${i + 1}" for i, (key, value) in enumerate(custom_params.items())])
            query = f"SELECT * FROM {self.table} WHERE {conditions}"
            return await self.fetch_query(query, return_one_record_list=True, *custom_params.values())
        elif id_value:
            return await self.fetch_query(f"SELECT * FROM {self.table} WHERE id = $1", id_value)

    async def delete(self, id_value: int) -> None:
        query = f"DELETE FROM {self.table} WHERE id = $1"
        await self.execute_query(query, id_value)

    @classmethod
    async def create_tables(cls):
        # Список запросов для создания таблиц
        table_creation_queries = (
            """
            CREATE TABLE IF NOT EXISTS users (
                id int PRIMARY KEY,
                username text,
                registered timestamp,
                lang text default 'en',
                time_zone text
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS notifications (
                id serial PRIMARY KEY,
                user_id int,
                description text,
                date_complete text,
                title text,
                is_on int default 1,
                date_set text,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS time_zones (
                id serial PRIMARY KEY,
                time_zone text
            );
            """
        )

        async with cls._pool.acquire() as conn:
            for query in table_creation_queries:
                await conn.execute(query)

    @classmethod
    async def make_migrations(cls):
        migration_queries = (
            """
            DROP TABLE time_zones;
            """,
            """
            CREATE TABLE IF NOT EXISTS time_zones (
                id serial PRIMARY KEY,
                time_zone text
            );
            """
        )

        async with cls._pool.acquire() as conn:
            for query in migration_queries:
                await conn.execute(query)
