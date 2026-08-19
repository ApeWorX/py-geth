import os
import shutil


def mkdir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def ensure_path_exists(dir_path: str) -> bool:
    """
    Make sure that a path exists
    """
    if not os.path.exists(dir_path):
        mkdir(dir_path)
        return True
    return False


def remove_file_if_exists(path: str) -> bool:
    if os.path.isfile(path):
        os.remove(path)
        return True
    return False


def remove_dir_if_exists(path: str) -> bool:
    if os.path.isdir(path):
        shutil.rmtree(path)
        return True
    return False


def is_executable_available(program: str) -> bool:
    return shutil.which(program) is not None


def is_same_path(p1: str, p2: str) -> bool:
    n_p1 = os.path.abspath(os.path.expanduser(p1))
    n_p2 = os.path.abspath(os.path.expanduser(p2))

    try:
        return os.path.samefile(n_p1, n_p2)
    except FileNotFoundError:
        return n_p1 == n_p2
