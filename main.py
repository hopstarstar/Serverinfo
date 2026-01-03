import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from python_aternos import Client, atserver

# Данные берутся из настроек Railway (Variables)
TOKEN = os.getenv('8206843283:AAEyckF1wIR1nweg0serfLqDhbIpXA6ol2Q')
ATERNOS_USER = os.getenv('eetrgtrty')
ATERNOS_PASS = os.getenv('06708539')

bot = Bot(token=TOKEN)
dp = Dispatcher()

def get_server_status():
    try:
        atclient = Client.from_credentials(ATERNOS_USER, ATERNOS_PASS)
        server = atclient.list_servers()[0]
        
        status_map = {
            atserver.Status.on: "✅ Онлайн",
            atserver.Status.off: "❌ Выключен",
            atserver.Status.starting: "⏳ Запускается...",
            atserver.Status.loading: "⌛ Загрузка...",
            atserver.Status.v_queue: "🚶 В очереди",
            atserver.Status.stopping: "🛑 Останавливается..."
        }
        
        current_status = status_map.get(server.status, "❓ Неизвестно")
        return server, current_status
    except Exception as e:
        return None, f"⚠️ Ошибка: {str(e)}"

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🔄 Обновить статус", callback_data="check_status"))
    builder.row(types.InlineKeyboardButton(text="🚀 Запустить сервер", callback_data="start_server"))
    
    await message.answer("🎮 **Управление Aternos**\nНажми кнопку ниже:", reply_markup=builder.as_markup(), parse_mode="Markdown")

@dp.callback_query(lambda c: c.data in ["check_status", "start_server"])
async def handle_buttons(callback_query: types.CallbackQuery):
    server, status_text = get_server_status()
    
    if not server:
        await callback_query.message.edit_text(status_text)
        return

    if callback_query.data == "start_server":
        if server.status == atserver.Status.off:
            server.start()
            status_text = "🚀 Запуск начат!"
        elif server.status == atserver.Status.on:
            status_text = "✅ Уже включен!"

    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🔄 Обновить статус", callback_data="check_status"))
    builder.row(types.InlineKeyboardButton(text="🚀 Запустить сервер", callback_data="start_server"))

    await callback_query.message.edit_text(
        f"Статус: **{status_text}**\nИгроков: `{server.players_count}/{server.slots}`",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await callback_query.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
