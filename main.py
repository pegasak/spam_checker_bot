import os
import glob
import asyncio

from checker.rar_utils import extract_rar
from checker.check_session import process_account


def extract_all_archives(input_dir="input", output_dir="sessions"):
    rar_files = glob.glob(os.path.join(input_dir, "*.rar"))

    if not rar_files:
        print("В папке input/ не найдено архивов.")
        return

    for rar_path in rar_files:
        result = extract_rar(rar_path)
        if result:
            print(f"Успешно распакован архив: {rar_path}")
        else:
            print(f"Ошибка при распаковке архива: {rar_path}")


async def run_all_sessions():
    session_paths = []
    for root, _, files in os.walk("sessions"):
        for file in files:
            if file.endswith(".json"):
                base_name = file.replace(".json", "")
                session_file = os.path.join(root, base_name + ".session")
                session_paths.append(session_file)

    if not session_paths:
        print("Не найдено ни одной сессии (.json + .session)")
        return

    tasks = []
    for i, session_path in enumerate(session_paths):
        tasks.append(asyncio.create_task(process_account(session_path, i)))

    results = await asyncio.gather(*tasks)

    blocked = sum(1 for r in results if r is True)
    clean = sum(1 for r in results if r is False)
    failed = sum(1 for r in results if r is None)

    print("\nРезультаты:")
    print(f"  Заблокировано: {blocked}")
    print(f"  Чистые: {clean}")
    print(f"  Ошибки: {failed}")


if __name__ == "__main__":
    print("Распаковка архивов...")
    extract_all_archives()

    print("\nПроверка сессий...")
    asyncio.run(run_all_sessions())
