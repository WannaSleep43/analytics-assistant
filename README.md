# Analytics Assistant — Text2SQL Helper

**Описание**  
Analytics Assistant — это интерактивный аналитический помощник для работы с базами данных.
Проект позволяет пользователям формулировать запросы на естественном языке, 
а система автоматически генерирует корректные SQL-запросы и возвращает результаты 
из базы данных `students.db`.  

Основная цель проекта — обучение генерации SQL-запросов с использованием LLM и тестирование
различных метрик качества этих генераций.  

---

## Основные возможности

- Генерация SQL-запросов из естественных текстовых запросов:
  - `naive` — базовая генерация с  
  - `description` — с учетом текстового описания структуры базы  
  - `meta` — с использованием метаданных таблиц и колонок  

---

## Структура проекта

analytics-assistant/ \
├─ main.py # FastAPI приложение \
├─ text2sql.py # Генерация SQL с LLM \
├─ data/ # Работа с БД, метаданные \
│ └─ students.db \
├─ errors/ # Поддерживаемые ошибки \
├─ tests/ \
│ ├─ test_cases.yaml # Тестовые кейсы \
│ └─ test.py # Скрипты для тестирования

---

## Метрики

| Модель              | naive (правильных/всего) | description | meta  |
|---------------------|--------------------------|-------------|-------|
| deepseek-coder-6.7b | 20/25                    | 22/25       | 23/25 |
| qwen2.5-coder-7b    | 22/25                    | 22/25       | 23/25 |

---

## Примеры работы

**Вопрос:**
> Какие кабинеты используются чаще всего? Покажи их по убыванию количества учеников, в случае совпадения — по возрастанию номера кабинета.

**SQL:**

```sql
SELECT classroom
FROM (
    SELECT classroom, COUNT(*) AS student_count
    FROM students
    GROUP BY classroom
) t
ORDER BY student_count DESC, classroom;
```

**Вопрос:**
> Найди класс, в котором учится, ребёнок, который учится хуже всех

**SQL:**

```sql
SELECT class
FROM students
ORDER BY avg_score
LIMIT 1;
```

---

## Запуск на macOS

### 1. Установить Ollama

```bash
brew install ollama
```

Запустить Ollama (в отдельном терминале или в фоне):

```bash
ollama serve
```

Скачать модель для генерации SQL:

```bash
ollama pull qwen2.5-coder:7b
```

Команда `ollama run` не нужна — она для интерактивного чата с моделью; приложению достаточно работающего сервера и скачанной модели.

### 2. Создать виртуальное окружение и установить зависимости

```bash
cd analytics-assistant
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Запустить приложение

```bash
python main.py
```

Swagger: **http://127.0.0.1:8000/docs**

---

## Предустановка (Linux, pacman)

```bash
sudo pacman -S ollama
ollama pull qwen2.5-coder:7b
ollama run qwen2.5-coder:7b
```