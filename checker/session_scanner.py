import os
from typing import List

def find_session_files(sessions_dir: str = "sessions") -> List[str]:
    """
    Находит все .session файлы в папке sessions/ и её подпапках.
    Возвращает список путей к этим файлам.
    """
    session_files = []
    for root, dirs, files in os.walk(sessions_dir):
        for file in files:
            if file.endswith(".session"):
                full_path = os.path.join(root, file)
                session_files.append(full_path)
    return session_files