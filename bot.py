from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# === Конфигурация ===
TOKEN = "8450971744:AAEyHw6T6de18xodzn9J5gqsQwyh8kfc4fI"  # ← вставь токен своего бота

# Фиксированные GEO позиции
GEO_POSITIONS = [
    "NPR",
    "BDT",
    "Асана, переключения, Рабочие, Контакты",
    "СНГ, LKR",
    "EGP, MAD",
    "PKR"
]

# Пул участников
joined_users = []

# === Команды ===

async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    username = f"@{user.username}" if user.username else user.first_name

    if username not in joined_users:
        joined_users.append(username)
        await update.message.reply_text(f"{username} присоединился к смене.")
    else:
        await update.message.reply_text(f"{username}, ты уже в списке.")

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not joined_users:
        await update.message.reply_text("❌ Никто не присоединился к смене.")
        return

    if len(joined_users) < len(GEO_POSITIONS):
        await update.message.reply_text("⚠️ Недостаточно людей для распределения всех GEO.")
        return

    lines = [f"{user} {geo}" for user, geo in zip(joined_users, GEO_POSITIONS)]
    await update.message.reply_text("\n".join(lines))

async def list_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not joined_users:
        await update.message.reply_text("📭 Пока никто не присоединился.")
        return

    members = "\n".join([f"{i+1}. {u}" for i, u in enumerate(joined_users)])
    await update.message.reply_text(f"👥 Участники смены:\n{members}")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    joined_users.clear()
    await update.message.reply_text("♻️ Список участников очищен.")

# === Запуск ===
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("join", join))
    app.add_handler(CommandHandler("roll", roll))
    app.add_handler(CommandHandler("list", list_members))
    app.add_handler(CommandHandler("reset", reset))
    print("✅ Бот запущен и слушает команды...")
    app.run_polling()

if __name__ == "__main__":
    main()
