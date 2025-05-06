'''from checker.session_scanner import find_session_files

if __name__ == "__main__":
    session_paths = find_session_files()
    for path in session_paths:
        print("Найдена сессия:", path)'''

from checker.rar_utils import extract_rar
def test_extract():
    archive_path_1 = "input/1 сб.rar"
    archive_path_2 = "input/1 без сб.rar"

    extracted_1 = extract_rar(archive_path_1)
    extracted_2 = extract_rar(archive_path_2)

    if extracted_1 and extracted_2:
        print(f"Архивы распакованы:\n- {extracted_1}\n- {extracted_2}")


if __name__ == "__main__":
    test_extract()