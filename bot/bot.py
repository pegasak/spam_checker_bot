from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
import asyncio
from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer("Привет! Отправь архив для проверки.")


@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def handle_document(message: types.Message):
    if message.document:
        # Скачиваем архив
        file_id = message.document.file_id
        file_info = await bot.get_file(file_id)
        file_path = file_info.file_path
        archive_path = f"input/{message.document.file_name}"

        await bot.download_file(file_path, archive_path)

        # Распаковка архива
        extracted_path = extract_rar(archive_path)
        if extracted_path:
            await message.answer("Архив распакован, начинаю обработку аккаунтов.")

            # Обработка аккаунтов
            session_paths = find_session_files(extracted_path)
            results = await asyncio.gather(*[process_account(session, i) for i, session in enumerate(session_paths)])

            blocked = sum(1 for r in results if r is True)
            clean = sum(1 for r in results if r is False)
            failed = sum(1 for r in results if r is None)

            await message.answer(f"📊 Результаты:\n  Заблокировано: {blocked}\n  Чистые: {clean}\n  Ошибки: {failed}")
        else:
            await message.answer("Не удалось распаковать архив.")


if __name__ == "__main__":
    from aiogram import executor

    executor.start_polling(dp)
