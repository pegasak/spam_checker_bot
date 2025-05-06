import os
import patoolib
import re
from typing import Optional

RAR_EXTRACT_DIR = "sessions"


def extract_rar(archive_path: str) -> Optional[str]:
    """
    Распаковывает RAR-архив в sessions/{имя_архива}/.
    """
    try:
        archive_name = os.path.splitext(os.path.basename(archive_path))[0]
        archive_name = re.sub(r'[^\wа-яА-Я]', '_', archive_name)

        extract_path = os.path.join(RAR_EXTRACT_DIR, archive_name)

        patoolib.extract_archive(archive_path, outdir=extract_path)

        entries = os.listdir(extract_path)
        if len(entries) == 1:
            nested_dir = os.path.join(extract_path, entries[0])
            if os.path.isdir(nested_dir):
                for file_name in os.listdir(nested_dir):
                    src = os.path.join(nested_dir, file_name)
                    dst = os.path.join(extract_path, file_name)
                    os.rename(src, dst)
                os.rmdir(nested_dir)

        return extract_path
    except Exception as e:
        print(f"Ошибка распаковки: {e}")
        return None