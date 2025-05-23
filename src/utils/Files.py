import os

class Files:

    @staticmethod
    def all_files_in_dir(path: str) -> list[str]:
        return [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    
    @staticmethod
    def check_if_file_exists(path: str) -> bool:
        return os.path.exists(path)
    
    @staticmethod
    def create_dir_if_not_exist(path: str) -> None:
        try:
            os.mkdir(path)
        except FileExistsError:
            pass
        except Exception as exc:
            raise exc