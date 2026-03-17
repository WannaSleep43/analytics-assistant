import ollama
import sqlglot

from errors.errors import SecurityException, BadGenerationException


async def text2sql(query: str, schema: str = "", fewshots: str = '') -> str:
    for i in range(3):
        query = await clean_sql(
            ollama.generate(
            # model='deepseek-coder:6.7b',
            model='qwen2.5-coder:7b',
            prompt=f"""
                Ты - SQL генератор, ты помогаешь аналитику составить SQL запрос в базу.
                
                Возвращай ТОЛЬКО SQL ЗАПРОС БЕЗ КОММЕНТАРИЕВ.
                
                Схема БД:
                {schema}
                
                Примеры хорошо выполненных работающих запросов:
                {fewshots}
                
                Вопрос аналитика:
                {query}
            """)['response']
        )

        try:
            statements = sqlglot.parse_one(query)

            if not isinstance(statements, sqlglot.exp.Select) :
                raise SecurityException("Попытка изменения таблицы запрещена.")

            return query
        except sqlglot.errors.ParseError:
            pass
    raise BadGenerationException('Не удалось сгенерировать корректный sql-запрос')

async def clean_sql(sql: str) -> str:
    sql = sql.strip()
    if sql.startswith('```'):
        return sql.strip('`')[3:]
    return sql