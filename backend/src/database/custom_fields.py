
from tortoise.fields.base import (
    Field,
)


class MyField(Field[int], int):
    """
    Autoincrement field
    """
    SEQ = "create sequence seq_t1 increment by 1 minvalue 300000" 
    SQL_TYPE = f"{SEQ}\nINT DEFAULT nextval('seq_t1')"
    # allows_generated = True

    def __init__(self, **kwargs) -> None:
        # kwargs["generated"] = bool(kwargs.get("generated", True))
        super().__init__(**kwargs)

    @property
    def constraints(self) -> dict:
        return {
            "ge": 1 if self.generated or self.reference else -2147483648,
            "le": 2147483647,
        }

    class _db_postgres:
        GENERATED_SQL = "SERIAL NOT NULL"

    class _db_sqlite:
        GENERATED_SQL = "INTEGER AUTOINCREMENT NOT NULL"

    class _db_mysql:
        GENERATED_SQL = "INT NOT NULL AUTO_INCREMENT"