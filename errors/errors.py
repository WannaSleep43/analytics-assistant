class Text2SQLException(Exception):
    """Custom exception class"""

class SecurityException(Text2SQLException):
    """Ошибка, отвечающая за попытку изменения БД."""

class BadGenerationException(Text2SQLException):
    """Ошибка, бросаемая в случае, если не удаётся сгенерировать валидный SQL-запрос."""