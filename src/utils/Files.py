import os

class Files:

    @staticmethod
    def all_files_in_dir(path: str) -> list[str]:
        return [os.path.isfile(os.path.join(path, f)) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]