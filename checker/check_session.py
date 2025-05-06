import os
import socks
import json
import asyncio
from telethon import TelegramClient
from telethon.errors import (
    SessionPasswordNeededError,
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
    FloodWaitError
)

API_ID = 21960371
API_HASH = '89dc67f0409e03d286d4bee6bc8accd2'

PROXIES = [
    ('pool.infatica.io', 10000, 'GUMP9RAtIs7yPHsS00OM', 'RNW78Fm5'),
    ('pool.infatica.io', 10001, 'GUMP9RAtIs7yPHsS00OM', 'RNW78Fm5'),
    ('pool.infatica.io', 10002, 'GUMP9RAtIs7yPHsS00OM', 'RNW78Fm5'),
    ('pool.infatica.io', 10003, 'GUMP9RAtIs7yPHsS00OM', 'RNW78Fm5'),
    ('pool.infatica.io', 10004, 'GUMP9RAtIs7yPHsS00OM', 'RNW78Fm5'),
    ('pool.infatica.io', 10005, 'GUMP9RAtIs7yPHsS00OM', 'RNW78Fm5'),
    ('pool.infatica.io', 10006, 'GUMP9RAtIs7yPHsS00OM', 'RNW78Fm5'),
    ('pool.infatica.io', 10007, 'GUMP9RAtIs7yPHsS00OM', 'RNW78Fm5'),
    ('pool.infatica.io', 10008, 'GUMP9RAtIs7yPHsS00OM', 'RNW78Fm5'),
    ('pool.infatica.io', 10009, 'GUMP9RAtIs7yPHsS00OM', 'RNW78Fm5'),
    ('pool.infatica.io', 10010, 'GUMP9RAtIs7yPHsS00OM', 'RNW78Fm5'),
    ('pool.infatica.io', 10011, 'GUMP9RAtIs7yPHsS00OM', 'RNW78Fm5'),
    ('pool.infatica.io', 10012, 'GUMP9RAtIs7yPHsS00OM', 'RNW78Fm5'),
    ('pool.infatica.io', 10013, 'GUMP9RAtIs7yPHsS00OM', 'RNW78Fm5'),
    ('pool.infatica.io', 10014, 'GUMP9RAtIs7yPHsS00OM', 'RNW78Fm5'),
    ('pool.infatica.io', 10015, 'GUMP9RAtIs7yPHsS00OM', 'RNW78Fm5'),
    ('pool.infatica.io', 10016, 'GUMP9RAtIs7yPHsS00OM', 'RNW78Fm5'),
    ('pool.infatica.io', 10017, 'GUMP9RAtIs7yPHsS00OM', 'RNW78Fm5'),
    ('pool.infatica.io', 10018, 'GUMP9RAtIs7yPHsS00OM', 'RNW78Fm5'),
    ('pool.infatica.io', 10019, 'GUMP9RAtIs7yPHsS00OM', 'RNW78Fm5'),
    ('pool.infatica.io', 10020, 'GUMP9RAtIs7yPHsS00OM', 'RNW78Fm5'),
    ('pool.infatica.io', 10021, 'GUMP9RAtIs7yPHsS00OM', 'RNW78Fm5'),
    ('pool.infatica.io', 10022, 'GUMP9RAtIs7yPHsS00OM', 'RNW78Fm5'),
    ('pool.infatica.io', 10023, 'GUMP9RAtIs7yPHsS00OM', 'RNW78Fm5'),
    ('pool.infatica.io', 10024, 'GUMP9RAtIs7yPHsS00OM', 'RNW78Fm5'),
    ('pool.infatica.io', 10025, 'GUMP9RAtIs7yPHsS00OM', 'RNW78Fm5'),
    ('pool.infatica.io', 10026, 'GUMP9RAtIs7yPHsS00OM', 'RNW78Fm5'),
    ('pool.infatica.io', 10027, 'GUMP9RAtIs7yPHsS00OM', 'RNW78Fm5'),
]


def get_proxy(index):
    host, port, login, password = PROXIES[index % len(PROXIES)]
    return (socks.SOCKS5, host, port, True, login, password)


def load_account_params(session_path: str) -> dict:
    json_path = session_path.replace('.session', '.json')
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"JSON-файл не найден: {json_path}")

    with open(json_path, 'r', encoding='utf-8') as f:
        params = json.load(f)

    return {
        'phone': params['phone'],
        'api_id': params['app_id'],
        'api_hash': params['app_hash'],
        'password': params.get('twoFA')
    }


async def create_new_session_from_json(session_path: str, proxy_index: int) -> bool:
    params = load_account_params(session_path)
    proxy = get_proxy(proxy_index)

    client = TelegramClient(
        session_path,
        params["api_id"],
        params["api_hash"],
        proxy=proxy
    )

    await client.connect()

    if await client.is_user_authorized():
        print(f"✅ {session_path} — уже авторизован")
        await client.disconnect()
        return True

    try:
        print(f"📲 Отправляю код на номер: {params['phone']}")
        await client.send_code_request(params["phone"])
        code = input(f"Введите код для {params['phone']}: ")

        await client.sign_in(phone=params["phone"], code=code)

    except SessionPasswordNeededError:
        if not params.get("password"):
            print(f"❌ {session_path} — требует пароль, но его нет в JSON")
            await client.disconnect()
            return False
        await client.sign_in(password=params["password"])

    except (PhoneCodeInvalidError, PhoneCodeExpiredError) as e:
        print(f"❌ Код неверный или истёк: {e}")
        await client.disconnect()
        return False

    except Exception as e:
        print(f"⚠️ Ошибка авторизации {params['phone']}: {e}")
        await client.disconnect()
        return False

    print(f"✅ Успешная авторизация {params['phone']}")
    await client.disconnect()
    return True


async def check_spamblock(client: TelegramClient) -> bool:
    try:
        async with client.conversation("SpamBot") as conv:
            await conv.send_message("/start")
            response = await conv.get_response()
            return "спам" in response.text.lower() or "ban" in response.text.lower()
    except Exception as e:
        print(f"⚠️ Ошибка @SpamBot: {e}")
        return False


async def process_account(session_path: str, proxy_index: int):
    try:
        if not os.path.exists(session_path):
            created = await create_new_session_from_json(session_path, proxy_index)
            if not created:
                return None  # Не удалось авторизовать

        params = load_account_params(session_path)
        proxy = get_proxy(proxy_index)

        client = TelegramClient(
            session_path,
            params["api_id"],
            params["api_hash"],
            proxy=proxy
        )

        await client.connect()

        if not await client.is_user_authorized():
            print(f"🔴 {session_path} — сессия недействительна")
            return None

        is_blocked = await check_spamblock(client)
        print(f"🔹 {session_path} — {'ЗАБЛОКИРОВАН' if is_blocked else 'Чистый'}")
        return is_blocked

    except Exception as e:
        print(f"⚠️ Ошибка при проверке {session_path}: {e}")
        return None
    finally:
        await client.disconnect()


if __name__ == "__main__":
    session_files = []
    for root, dirs, files in os.walk("sessions"):
        for file in files:
            if file.endswith(".json"):  # работаем по JSON-файлам
                base = file.replace(".json", "")
                session_path = os.path.join(root, base + ".session")
                session_files.append(session_path)

    async def main():
        tasks = []
        for i, session_path in enumerate(session_files):
            task = asyncio.create_task(process_account(session_path, i))
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        blocked = sum(1 for r in results if r is True)
        clean = sum(1 for r in results if r is False)
        failed = sum(1 for r in results if r is None)

        print(f"\n📊 Результаты:")
        print(f"  🔒 Заблокировано: {blocked}")
        print(f"  ✅ Чистые: {clean}")
        print(f"  ⚠️ Ошибки: {failed}")

    asyncio.run(main())
