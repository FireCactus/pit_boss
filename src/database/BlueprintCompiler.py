import re
from typing import *
import os
from collections import defaultdict, deque

from utils.Loc import Loc
from utils.Files import Files

class Action(NamedTuple):
    delete: Optional[str]
    update: Optional[str]

class TableColumnScheme(NamedTuple):
    name: str
    type: str
    restricions: Optional[List[str]]
    relation: Optional[str]
    on_action: Optional[Action]

class TableScheme(NamedTuple):
    name: str
    columns: List[TableColumnScheme]

class DatabaseScheme(NamedTuple):
    tables: List[TableScheme]

class InvalidBlueprint(Exception):
    pass

VALID_ACTIONS = {"CASCADE", "SET NULL", "SET DEFAULT", "RESTRICT", "NO ACTION"}

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

            name: str = parts[0]
            col_type: str = parts[1]
            restrictions: Optional[List[str]] = parts[2].strip('"').split(',') if len(parts) > 2 and parts[2] != "" else None
            relation: Optional[str] = parts[3] if len(parts) > 3 and parts[3] != "" else None
            actions: Optional[List[str]] = parts[4].strip('"').split('/') if len(parts) > 4 and parts[4] != "" else None
            
            on_action: Optional[Action]
            if actions is not None:
                delete: Optional[str] = self._validate_action(actions[0]) if len(actions) > 0 else None
                update: Optional[str] = self._validate_action(actions[1]) if len(actions) > 1 else None
                on_action = Action(delete, update)
            else:
                on_action = None
            

            cols.append(TableColumnScheme(name, col_type, restrictions, relation, on_action))

        table_name = os.path.splitext(os.path.basename(file_path))[0]
        return TableScheme(name=table_name, columns=cols)
    

    def _validate_action(self, a: Optional[str]) -> Optional[str]:
        if a and a.upper() not in VALID_ACTIONS:
            raise InvalidBlueprint(f"Invalid ON DELETE/UPDATE action: {a}")
        return a.upper() if a else None

    def __topological_sort_tables(self, tables: List[TableScheme]) -> List[TableScheme]:
        table_map: Dict[str, TableScheme] = {table.name: table for table in tables}
        dependencies: Dict[str, Set[str]] = defaultdict(set)

        for table in tables:
            for col in table.columns:
                if col.relation:
                    match = re.match(r"(\w+)\(\w+\)", col.relation)
                    if match:
                        referenced_table = match.group(1)
                        dependencies[table.name].add(referenced_table)

        in_degree: Dict[str, int] = {name: 0 for name in table_map.keys()}
        for table_dep, deps in dependencies.items():
            in_degree[table_dep] = len(deps)

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