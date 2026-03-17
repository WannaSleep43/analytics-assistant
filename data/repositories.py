from pathlib import Path

import aiosqlite

from data.databases import DBList

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data"

async def create_repo():
    repositories = dict()
    for name in DBList.__members__:
        repositories[name] = CommonRepository()
        await repositories[name].open(name)
    return repositories

class CommonRepository:
    def __init__(self):
        self.connect: None | aiosqlite.Connection = None
        self.closed: bool = False
        self.columns = None

    async def open(self, basename: str):
        self.connect = await aiosqlite.connect(DATA_PATH/ f"{basename}.db")

    async def execute_query(self, query: str):
        async with self.connect.cursor() as cursor:
            q = await cursor.execute(query)
            return await q.fetchall()

    async def described_execute_query(self, query: str):
        async with self.connect.cursor() as cursor:

            q = await cursor.execute(query)
            description = [col[0] for col in cursor.description]
            rows = await q.fetchall()

            return [dict(zip(description, row)) for row in rows]

    async def close(self):
        await self.connect.commit()
        await self.connect.close()

class HistoryRepository(CommonRepository):
    def __init__(self):
        super().__init__()

    async def insert_row(self, query: str, query_type: str, generation: str | None, status: str):
        async with self.connect.cursor() as cursor:
            await cursor.execute("INSERT INTO history "
                                 "(query, query_type, generation, status) "
                                 "VALUES (?, ?, ?, ?);",
                                 (query, query_type, generation, status))
            await self.connect.commit()