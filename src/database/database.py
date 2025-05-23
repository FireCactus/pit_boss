from typing import *
from abc import ABC, abstractmethod
import sqlite3

from database.BlueprintCompiler import BlueprintCompiler, TableScheme, DatabaseScheme
from utils.Loc import Loc
from utils.Files import Files
from utils.Singleton import Singleton


class Database(metaclass=Singleton):

    __name: str
    _cursor: sqlite3.Cursor

    def __init__(self, name: str) -> None:
        self.__name = name
        self._cursor = sqlite3.connect(f"{Loc.datahub(self.__name)}.db").cursor()
        self.sanity_check()

    def sanity_check(self) -> None:
        # if not Files.check_if_file_exists(Loc.datahub(self.__name)):
        bc: BlueprintCompiler = BlueprintCompiler()
        self.__recreate_from_scheme(bc.database_scheme_from_blueprints(self.__name))

    def __recreate_from_scheme(self, db_scheme: DatabaseScheme) -> None:
        for ts in db_scheme:
            self._cursor.execute(self.__sql_str_from_table_scheme(ts))

    def __sql_str_from_table_scheme(self, ts: TableScheme) -> str:
        cols = ", ".join([f"{col.name} {col.type}"for col in ts.columns])
        query = f"CREATE TABLE {ts.name}({cols})"
        return query
            