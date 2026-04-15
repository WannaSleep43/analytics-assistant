from pathlib import Path
import yaml

from data.databases import DBList

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data"

def collect_description(db: DBList):
    with (DATA_PATH / f'{db.value}_description.txt').open() as f:
        return ''.join(f.readlines())

TAB_SIZE = 2

def collect_meta(db: DBList) -> tuple[str, str]:
    with (DATA_PATH / f'{db.value}_metadata.yaml').open() as f:
        data = yaml.safe_load(f)

        schema: str = ''

        for table, table_meta in data['schema'].items():
            schema += f'Table {table}\n'
            schema += f"{' ' * TAB_SIZE}description: {table_meta['description']}\n"

            for column, description in table_meta['columns'].items():
                schema += f'{" " * 2 * TAB_SIZE + column}: {description}\n'
            schema += '\n'

        fewshots: str = ''

        for line in data['fewshots']:
            fewshots += f"[Вопрос]: {line['question']}\n"
            fewshots += f"[Ответ]: ```sql\n{line['answer']}\n```\n"

        return schema, fewshots
