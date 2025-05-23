import re
from typing import *
import os

from utils.Loc import Loc
from utils.Files import Files


class TableColumnScheme(NamedTuple):
    name: str
    type: str
    relation: Optional[str]

class InvalidBlueprint(Exception):
    pass

class TableScheme(NamedTuple):
    name: str
    columns: List[TableColumnScheme]

DatabaseScheme = List[TableScheme]

@final
class BlueprintCompiler:

    __blueprint_path: Final[str] = Loc.src("database", "blueprints")

    def database_scheme_from_blueprints(self, database_name: str) -> DatabaseScheme:
        ptb: DatabaseScheme = []

        for blueprint in Files.all_files_in_dir(os.path.join(self.__blueprint_path, database_name)):
            ptb.append(self.__parse_table_blueprint(blueprint))

        return ptb


    def __parse_table_blueprint(self, file_path: str) -> TableScheme:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines: List[str] = f.readlines()

        pattern = re.compile(r'(\S+)\s+(\S+)(?:\s+(\S+))?')

        cols: List[TableColumnScheme] = []

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            match = pattern.match(line)
            if match:
                column: str = match.group(1)
                col_type: str = match.group(2)
                relations: Optional[str] = match.group(3) if match.group(3) else None
                cols.append(TableColumnScheme(column, col_type, relations))
            else:
                raise InvalidBlueprint(f"Invalid database table blueprint: {file_path}")

        return TableScheme(name=os.path.basename(file_path), columns=cols)