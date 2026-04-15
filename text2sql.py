import ollama
import sqlglot

from errors.errors import SecurityException, BadGenerationException


async def text2sql(query: str, schema: str = "", fewshots: str = '') -> str:
    for i in range(3):
        query = await clean_sql(
            ollama.generate(
            model='deepseek-coder:6.7b',
            # model='qwen2.5-coder:7b',
            options={
                "temperature": 0.1
            },
            prompt=f"""
                Ты опытный аналитик данных. Ты помогаешь пользователю составить SQL запрос в соответствии с его требованием.
                
                Обрати внимание, что в ответ нужно вывести ТОЛЬКО ожидаемый SQL запрос.
                
                Схема базы данных:
                {schema}
                
                Примеры хорошо составленных запросов:
                {fewshots}
                
                [Вопрос]: {query}
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
    start = sql.find('```sql')
    end = sql.rfind('```')

    if start == -1 or end == -1 or end <= start:
        return sql

    return sql[start + 6:end].strip()