import re
from typing import *
import os

from utils.Loc import Loc
from utils.Files import Files


class TableColumnScheme(NamedTuple):
    name: str
    type: str
    restricions: Optional[str]
    relation: Optional[str]

class TableScheme(NamedTuple):
    name: str
    columns: List[TableColumnScheme]

class DatabaseScheme(NamedTuple):
    tables: List[TableScheme]

class InvalidBlueprint(Exception):
    pass

@final
class BlueprintCompiler:

    __blueprint_path: Final[str] = Loc.src("database", "blueprints")

    def database_scheme_from_blueprints(self, database_name: str) -> DatabaseScheme:
        tables: List[TableScheme] = []

        for blueprint in Files.all_files_in_dir(os.path.join(self.__blueprint_path, database_name)):
            tables.append(self.__parse_table_blueprint(blueprint))

        return DatabaseScheme(tables)
        
        
    def __parse_table_blueprint(self, file_path: str) -> TableScheme:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines: List[str] = f.readlines()

        cols: List[TableColumnScheme] = []

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            parts = re.split(r'\s{2,}', line)

            if len(parts) < 2:
                raise InvalidBlueprint(f"Invalid blueprint line in: {file_path} → '{line}'")

            name = parts[0]
            col_type = parts[1]
            restrictions = parts[2].strip('"') if len(parts) > 2 and parts[2] else None
            relation = parts[3] if len(parts) > 3 and parts[3] else None

            cols.append(TableColumnScheme(name, col_type, restrictions, relation))

        table_name = os.path.splitext(os.path.basename(file_path))[0]
        return TableScheme(name=table_name, columns=cols)