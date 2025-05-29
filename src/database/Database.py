from typing import *
from abc import ABC
import sqlite3


from database.BlueprintCompiler import BlueprintCompiler, TableScheme, DatabaseScheme, TableColumnScheme, Action
from utils.Loc import Loc
from utils.Files import Files
from utils.Singleton import Singleton


class Database(metaclass=Singleton):

    _name: str
    _cursor: sqlite3.Cursor

    def __init__(self, name: str) -> None:
        self._name = name
        Files.create_dir_if_not_exist(Loc.datahub())
        self._cursor = sqlite3.connect(f"{Loc.datahub(self._name)}.db").cursor()
        self.sanity_check()

    def sanity_check(self) -> None:
        db_scheme: DatabaseScheme = BlueprintCompiler().database_scheme_from_blueprints(self._name)
        self.__synchronize(db_scheme)

    def __synchronize(self, loaded_scheme: DatabaseScheme) -> None:
        existing_tables: Dict[str, TableScheme] = self.__load_current_schema()

        for table in loaded_scheme.tables:
            current = existing_tables.get(table.name)
            if current is None:
                self._cursor.execute(self.__generate_create_sql(table))
            elif not self.__compare_tables(current, table):
                self.__rebuild_table(current, table)

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
            fk_info = self._cursor.fetchall()

            foreign_keys = {
                row[3]: (row[2], row[6], row[5])  # from_col -> (to_table, on_delete, on_update)
                for row in fk_info
            }

            columns = []
            for col in col_info:
                col_name = col[1]
                col_type = col[2]

                restrictions = []
                if col[5]:  # pk
                    restrictions.append("PRIMARY KEY")
                if col[3]:  # not null
                    restrictions.append("NOT NULL")
                if col[4] is not None:
                    restrictions.append(f"DEFAULT {col[4]}")

                fk_tuple = foreign_keys.get(col_name)
                if fk_tuple:
                    relation = f"{fk_tuple[0]}(id)"  # <- zakładam klucz obcy do `id`
                    on_action = Action(
                        delete=fk_tuple[1] if fk_tuple[1] != "NO ACTION" else None,
                        update=fk_tuple[2] if fk_tuple[2] != "NO ACTION" else None
                    )
                else:
                    relation = None
                    on_action = None

                column = TableColumnScheme(
                    name=col_name,
                    type=col_type,
                    restricions=restrictions if restrictions else None,
                    relation=relation,
                    on_action=on_action
                )
                columns.append(column)

            tables[name] = TableScheme(name=name, columns=columns)

        return tables

    def __compare_tables(self, current: TableScheme, expected: TableScheme) -> bool:
        if len(current.columns) != len(expected.columns):
            return False

        for c1, c2 in zip(current.columns, expected.columns):
            if (
                c1.name != c2.name or
                c1.type.lower() != c2.type.lower() or
                (c1.restricions or []) != (c2.restricions or []) or
                (c1.relation or "") != (c2.relation or "") or
                (c1.on_action or Action(None, None)) != (c2.on_action or Action(None, None))
            ):
                return False

        return True

    def __generate_create_sql(self, table: TableScheme) -> str:
        column_defs: List[str] = []
        foreign_keys: List[str] = []

        for col in table.columns:
            col_def = f"{col.name} {col.type}"
            if col.restricions:
                col_def += " " + " ".join(col.restricions)
            column_defs.append(col_def)

            if col.relation:
                fk = f"FOREIGN KEY({col.name}) REFERENCES {col.relation}"
                if col.on_action:
                    if col.on_action.delete:
                        fk += f" ON DELETE {col.on_action.delete}"
                    if col.on_action.update:
                        fk += f" ON UPDATE {col.on_action.update}"
                foreign_keys.append(fk)

        all_defs = column_defs + foreign_keys
        joined_defs = ",\n  ".join(all_defs)
        return f"CREATE TABLE {table.name} (\n  {joined_defs}\n);"

    def __rebuild_table(self, current: TableScheme, expected: TableScheme) -> None:
        old_table = f"{current.name}_old"
        self._cursor.execute(f"ALTER TABLE {current.name} RENAME TO {old_table};")
        self._cursor.execute(self.__generate_create_sql(expected))

        old_cols = {col.name for col in current.columns}
        new_cols = {col.name for col in expected.columns}
        common_cols = list(old_cols & new_cols)

        if common_cols:
            col_list = ', '.join(common_cols)
            self._cursor.execute(f"""
                INSERT INTO {expected.name} ({col_list})
                SELECT {col_list} FROM {old_table};
            """)

        self._cursor.execute(f"DROP TABLE {old_table};")

