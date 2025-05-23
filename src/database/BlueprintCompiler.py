import re
from typing import *
import os
from collections import defaultdict, deque

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

        return DatabaseScheme(self.__topological_sort_tables(tables))
        
        
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
    

    def __topological_sort_tables(self, tables: List[TableScheme]) -> List[TableScheme]:
        table_map: Dict[str, TableScheme] = {table.name: table for table in tables}
        dependencies: Dict[str, Set[str]] = defaultdict(set)

        # Zbuduj zależności
        for table in tables:
            for col in table.columns:
                if col.relation:
                    match = re.match(r"(\w+)\(\w+\)", col.relation)
                    if match:
                        referenced_table = match.group(1)
                        dependencies[table.name].add(referenced_table)

        # Uzupełnij brakujące wpisy
        for name in table_map:
            dependencies.setdefault(name, set())

        # Oblicz in-degree (ile tabel każda zależy od innych)
        in_degree: Dict[str, int] = {name: 0 for name in table_map}
        for table, deps in dependencies.items():
            in_degree[table] = len(deps)

        # Zacznij od tabel bez zależności
        queue = deque([name for name, deg in in_degree.items() if deg == 0])
        sorted_names: List[str] = []

        while queue:
            current = queue.popleft()
            sorted_names.append(current)

            for dependent, deps in dependencies.items():
                if current in deps:
                    deps.remove(current)
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)

        if len(sorted_names) != len(tables):
            raise ValueError("Cycle in database!")

        return [table_map[name] for name in sorted_names]