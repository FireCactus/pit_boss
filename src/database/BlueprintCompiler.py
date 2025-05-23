import re
from typing import *

from utils.Loc import Loc
from utils.Files import Files


class TableColumnSchema(NamedTuple):
    name: str
    type: str
    relation: Optional[str]

class InvalidBlueprint(Exception):
    pass

TableSchema = List[TableColumnSchema]
DatabaseSchema = List[TableSchema]

@Final
class BlueprintCompiler:

    __blueprint_path: Final[str] = Loc.src("databse", "blueprints")

    def table_schema_from_blueprints(self) -> DatabaseSchema:
        ptb: DatabaseSchema = []

        for blueprint in Files.all_files_in_dir(self.__blueprint_path):
            ptb.append(self.__parse_table_blueprint(blueprint))

        return ptb


    def __parse_table_blueprint(file_path: str) -> TableSchema:

        with open(file_path, 'r', encoding='utf-8') as f:
            lines: List[str] = f.readlines()

        pattern = re.compile(r'(\S+)\s+(\S+)(?:\s+(\S+))?')

        schema: List[TableColumnSchema] = []

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            match = pattern.match(line)
            if match:
                column: str = match.group(1)
                col_type: str = match.group(2)
                relations: Optional[str] = match.group(3) if match.group(3) else None
                schema.append(TableColumnSchema(column, col_type, relations))
            else:
                raise InvalidBlueprint(f"Invalid database table blueprint: {file_path}")

        return schema