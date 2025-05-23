from typing import *
from abc import ABC
import sqlite3


from database.BlueprintCompiler import BlueprintCompiler, TableScheme, DatabaseScheme, TableColumnScheme
from utils.Loc import Loc
from utils.Files import Files
from utils.Singleton import Singleton


class Database(ABC, metaclass=Singleton):

    __name: str
    _cursor: sqlite3.Cursor

    def __init__(self, name: str) -> None:
        self.__name = name
        Files.create_dir_if_not_exist(Loc.datahub())
        self._cursor = sqlite3.connect(f"{Loc.datahub(self.__name)}.db").cursor()
        self.sanity_check()


    def sanity_check(self) -> None:
        db_scheme: DatabaseScheme = BlueprintCompiler().database_scheme_from_blueprints(self.__name)
        self.__synchronize(db_scheme)


    def __synchronize(self, loaded_scheme: DatabaseScheme) -> None:

        existing_tables: Dict[str, TableScheme] = self.__load_current_schema()

        for table in loaded_scheme.tables:
            current = existing_tables.get(table.name)
            if current == None:
                self._cursor.execute(self.__generate_create_sql(table))
            elif not self.__compare_tables(current, table):
                self.__rebuild_table( current, table)

        self._cursor.connection.commit()
        self._cursor.connection.close()


    def __load_current_schema(self) -> Dict[str, TableScheme]:

        self._cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        
        tables: Dict[str, TableScheme] = {}
        for (name,) in self._cursor.fetchall():
            if name.startswith("sqlite_"):
                continue
            
            self._cursor.execute(f"PRAGMA table_info({name});")
            col_info = self._cursor.fetchall()

            self._cursor.execute(f"PRAGMA foreign_key_list({name});")
            foreign_keys = {row[3]: row[2] for row in self._cursor.fetchall()}
            
            columns = []
            for col in col_info:
                col_name, col_type = col[1], col[2]
                relation = foreign_keys.get(col_name)
                columns.append(TableColumnScheme(col_name, col_type, relation))

            tables[name] = TableScheme(name, columns)

        return tables


    def __compare_tables(self, current: TableScheme, expected: TableScheme) -> bool:
        if len(current.columns) != len(expected.columns):
            return False
        
        for c1, c2 in zip(current.columns, expected.columns):
            if (c1.name != c2.name or
                c1.type.lower() != c2.type.lower() or
                c1.relation != c2.relation):
                return False
            
        return True


    def __generate_create_sql(self, table: TableScheme) -> str:
        columns_sql = []
        for col in table.columns:
            col_def = f"{col.name} {col.type}"
            if col.relation:
                col_def += f" REFERENCES {col.relation}"
            columns_sql.append(col_def)
        return f"CREATE TABLE {table.name} ({', '.join(columns_sql)});"


    def __rebuild_table(self, current: TableScheme, expected: TableScheme) -> None:
        old_table = f"{current.name}_old"
        self._cursor.execute(f"ALTER TABLE {current.name} RENAME TO {old_table};")
        self._cursor.execute(self.__generate_create_sql(expected))

        old_cols = {col.name for col in current.columns}
        new_cols = {col.name for col in expected.columns}
        common_cols = list(old_cols & new_cols)

        if len(common_cols) != 0:
            col_list = ', '.join(common_cols)
            self._cursor.execute(f"""
                INSERT INTO {expected.name} ({col_list})
                SELECT {col_list} FROM {old_table};
            """)
            
        self._cursor.execute(f"DROP TABLE {old_table};")
