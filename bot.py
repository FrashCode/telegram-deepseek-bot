#!/usr/bin/env python3
"""
Telegram бот на базе DeepSeek AI
Бесплатный аналог ChatGPT
"""

import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# ============= НАСТРОЙКИ =============
# Токены берутся из переменных окружения Render
TELEGRAM_TOKEN = os.environ.get(8765948951:AAGoubgsTqnekzPGE8jb7I0LBs9udYlOajk)
DEEPSEEK_API_KEY = os.environ.get(sk-dd399f95f69e4490a7e394139a8dff60)

# Проверка наличия токенов
if not TELEGRAM_TOKEN:
    raise ValueError("❌ Переменная TELEGRAM_TOKEN не установлена!")
if not DEEPSEEK_API_KEY:
    raise ValueError("❌ Переменная DEEPSEEK_API_KEY не установлена!")

# Настройка клиента DeepSeek (использует совместимое с OpenAI API)
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Словарь для хранения истории диалогов
user_histories = {}

# Максимум сообщений в истории (чтобы не перегружать память)
MAX_HISTORY = 20

# Системный промпт — задаёт характер бота
SYSTEM_PROMPT = """Ты — DeepSeek, дружелюбный и полезный AI-помощник. 
Ты создан китайской компанией DeepSeek.
Отвечай на русском языке кратко, понятно и по делу.
Будь вежливым и помогай пользователю решать его задачи."""

# ============= ФУНКЦИИ =============

def get_history(user_id):
    """Получить историю диалога пользователя"""
    if user_id not in user_histories:
        # Создаём новую историю с системным промптом
        user_histories[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    return user_histories[user_id]

def trim_history(history):
    """Обрезаем историю, оставляя только последние сообщения"""
    if len(history) > MAX_HISTORY + 1:  # +1 для system сообщения
        # Оставляем system (первое) и последние MAX_HISTORY сообщений
        return [history[0]] + history[-(MAX_HISTORY):]
    return history

async def get_deepseek_response(user_id, user_message):
    """Получить ответ от DeepSeek API"""
    try:
        # Получаем историю пользователя
        history = get_history(user_id)
        
        # Добавляем новое сообщение пользователя
        history.append({"role": "user", "content": user_message})
        
        # Обрезаем историю, если она слишком длинная
        history = trim_history(history)
        user_histories[user_id] = history
        
        # Запрос к DeepSeek API
        response = client.chat.completions.create(
            model="deepseek-chat",  # Бесплатная модель DeepSeek
            messages=history,
            max_tokens=2000,
            temperature=0.7,  # 0 = строго, 1 = креативно
        )
        
        # Получаем ответ
        assistant_message = response.choices[0].message.content
        
        # Сохраняем ответ в историю
        history.append({"role": "assistant", "content": assistant_message})
        user_histories[user_id] = trim_history(history)
        
        return assistant_message
        
    except Exception as e:
        logger.error(f"❌ Ошибка при запросе к DeepSeek: {e}")
        return "😔 Извините, произошла ошибка. Попробуйте позже."

async def clear_history(user_id):
    """Очистить историю диалога пользователя"""
    user_histories[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]

# ============= ОБРАБОТЧИКИ КОМАНД =============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    user_id = update.effective_user.id
    await clear_history(user_id)
    await update.message.reply_text(
        "🤖 **Привет! Я DeepSeek AI помощник!**\n\n"
        "Я бесплатный аналог ChatGPT от китайской компании DeepSeek.\n\n"
        "✨ **Что я умею:**\n"
        "• Отвечать на вопросы\n"
        "• Помогать с задачами\n"
        "• Поддерживать диалог\n"
        "• Помнить контекст разговора\n\n"
        "📌 **Команды:**\n"
  "/start — начать заново\n"
        "/clear — очистить историю\n"
        "/help — помощь\n\n"
        "💬 **Просто напиши мне сообщение!**",
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help"""
    await update.message.reply_text(
        "📖 **Как пользоваться ботом:**\n\n"
        "1️⃣ Просто отправь любое сообщение\n"
        "2️⃣ Я помню историю нашего разговора\n"
        "3️⃣ /clear — очистить память\n"
        "4️⃣ /start — начать новый диалог\n\n"
        "⚡ **Особенности:**\n"
        "• Работаю 24/7 на бесплатном хостинге\n"
        "• Использую бесплатную нейросеть DeepSeek\n"
        "• Нет ограничений на количество запросов\n\n"
        "❓ **Вопросы?** Просто спроси меня!",
        parse_mode="Markdown"
    )

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /clear — очистить историю"""
    user_id = update.effective_user.id
    await clear_history(user_id)
    await update.message.reply_text(
        "🧹 **История диалога очищена!**\n\n"
        "Теперь мы можем начать разговор заново.",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений"""
    user_id = update.effective_user.id
    user_message = update.message.text
    
    # Показываем, что бот "печатает"
    await update.message.chat.send_action(action="typing")
    
    # Получаем ответ от DeepSeek
    response = await get_deepseek_response(user_id, user_message)
    
    # Отправляем ответ
    await update.message.reply_text(response)

# ============= ЗАПУСК БОТА =============

def main():
    """Запуск бота"""
    # Создаём приложение
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Регистрируем обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("clear", clear))
    
    # Обработчик текстовых сообщений
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаем бота
    logger.info("🤖 Бот DeepSeek запущен и готов к работе!")
    print("🤖 Бот DeepSeek запущен и готов к работе!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
