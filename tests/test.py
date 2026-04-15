from pathlib import Path

import yaml
import pytest
import sqlite3
import pandas as pd

from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parent.parent
TEST_CASES_PATH = BASE_DIR / "tests" / "test_cases.yaml"
DB_PATH = BASE_DIR / "data" / "students.db"

GENERATORS = ['naive', 'description', 'meta']
test_stats = {gen: {"passed": 0, "total": 0} for gen in GENERATORS}

@pytest.fixture(scope='session')
def db():
    with sqlite3.connect(DB_PATH) as con:
        yield con

    print("\n=== Text2SQL Test Statistics ===")
    for gen, stats in test_stats.items():
        total = stats["total"]
        passed = stats["passed"]
        print(f"{gen}: {passed}/{total} passed ({passed/total*100:.1f}%)")
    print("===============================")

@pytest.fixture(scope='session')
def client():
    from main import app
    with TestClient(app) as c:
        yield c

def load_tests():
    with TEST_CASES_PATH.open() as f:
        data = yaml.safe_load(f)
        return data["tests"]

@pytest.mark.asyncio
@pytest.mark.parametrize("case", load_tests())
@pytest.mark.parametrize("generator", GENERATORS, ids=GENERATORS)
async def test_text2sql(case, db, client, generator):
    test_stats[generator]["total"] += 1

    question = case["question"]
    expected_sql = case["expected_sql"]

    response = client.post(f'/ai_query/{generator}/students?query={question}')
    assert response.status_code == 200
    generated_sql = response.json()['result']

    cursor = db.cursor()
    try:
        expected_query = cursor.execute(expected_sql)
        expected_result = expected_query.fetchall()
        expected_df = pd.DataFrame(expected_result)
    except sqlite3.Error:
        pytest.fail(f"Expected SQL execution failed.")

    try:
        generated_query = cursor.execute(generated_sql)
        generated_result = generated_query.fetchall()
        generated_df = pd.DataFrame(generated_result)
    except sqlite3.Error as e:
        pytest.fail(f"Generated SQL execution failed:{e}\nquestion: {question}\nquery: {generated_sql}")


    expected_set = set(tuple(expected_df.iloc[:, i]) for i in range(expected_df.shape[1]))
    generated_set = set(tuple(generated_df.iloc[:, i]) for i in range(generated_df.shape[1]))

    if expected_set.intersection(generated_set) != expected_set:
        pytest.fail(f'Question: {question}\nGenerated SQL:\n {generated_sql}')

    test_stats[generator]["passed"] += 1