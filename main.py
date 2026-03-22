import sqlite3
from contextlib import asynccontextmanager

import uvicorn

from errors.errors import SecurityException, BadGenerationException
from text2sql import text2sql
from fastapi import FastAPI, HTTPException
from data.databases import DBList
from data.collect_meta import collect_description, collect_meta
from data.repositories import create_repo, CommonRepository, HistoryRepository

repositories: None | dict[DBList, CommonRepository] = None
history: None | HistoryRepository = None

@asynccontextmanager
async def lifespan(_: FastAPI):
    global repositories, history
    repositories = await create_repo()

    history = HistoryRepository()
    await history.open('history')

    yield

    for key, repository in repositories.items():
        await repository.close()
    await history.close()

app = FastAPI(lifespan=lifespan)

@app.post("/query/{base}")
async def execute_query(base: DBList, query: str):
    try:
        result = await repositories[base].described_execute_query(query)
        return {'result': result}
    except sqlite3.Error as e:
        raise HTTPException(status_code=400, detail=str(e))

async def ai_query(base: DBList, query: str, description: str = '', fewshots = '', query_type = 'naive') -> dict:
    try:
        result = await text2sql(query, description, fewshots)

        try:
            response = await execute_query(base, result)
        except HTTPException:
            response = None

        await history.insert_row(query, query_type, result, 'ok')

        return {'result': result, 'response': response}
    except sqlite3.Error as e:
        await history.insert_row(query, query_type, None, 'syntax-error')
        raise HTTPException(status_code=400, detail=str(e))
    except SecurityException as e:
        await history.insert_row(query, query_type, None, 'security-error')
        raise HTTPException(status_code=401, detail=str(e))
    except BadGenerationException as e:
        await history.insert_row(query, query_type, None, 'bad-generation')
        raise HTTPException(status_code=402, detail=str(e))

@app.post("/ai_query/naive/{base}")
async def naive_ai_query(base: DBList, query: str) -> dict:
    return await ai_query(base, query, collect_description(base), query_type='naive')

@app.post("/ai_query/description/{base}")
async def description_ai_query(base: DBList, query: str) -> dict:
    return await ai_query(base, query, collect_meta(base)[0], query_type='description')

@app.post("/ai_query/meta/{base}")
async def meta_ai_query(base: DBList, query: str) -> dict:
    # prepare description
    description, fewshots = collect_meta(base)
    return await ai_query(base, query, description, fewshots, query_type='naive')

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)

