import os

project_root: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Loc:

    @staticmethod
    def datahub(*args: str) -> str:
        return os.path.join(project_root, "datahub", *args)

    @staticmethod
    def jar(*args: str) -> str:
        return os.path.join(project_root, "datahub", "jar", *args)
    
    @staticmethod
    def media(*args: str) -> str:
        return os.path.join(project_root, "media", *args)
    
    @staticmethod
    def src(*args: str) -> str:
        return os.path.join(project_root, "src", *args)

