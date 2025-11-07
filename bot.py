from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import random

# === Конфигурация ===
TOKEN = "8450971744:AAEyHw6T6de18xodzn9J5gqsQwyh8kfc4fI"  # ← вставь сюда токен

# === Глобальные переменные ===
joined_users = []

# === Гео и правила распределения ===
GEO_RULES = {
    "NPR": "attachable",
    "BDT": "attachable",
    "Асана, переключения, Рабочие, Контакты": "fixed",
    "СНГ, LKR": "fixed",
    "EGP, MAD": "splittable",
    "PKR": "attachable"
}


# === Команды ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎰 Привет! Я бот для распределения GEO по смене.\n\n"
        "Доступные команды:\n"
        "/join — присоединиться к игре\n"
        "/list — посмотреть участников\n"
        "/roll — распределить GEO\n"
        "/reset — очистить список"
    )


async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    username = f"@{user.username}" if user.username else user.first_name

    if username not in joined_users:
        joined_users.append(username)
        await update.message.reply_text(f"{username} присоединился к игре.")
    else:
        await update.message.reply_text(f"{username}, ты уже в списке.")


async def list_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not joined_users:
        await update.message.reply_text("📭 Пока никто не присоединился.")
        return

    members = "\n".join([f"{i+1}. {u}" for i, u in enumerate(joined_users)])
    await update.message.reply_text(f"👥 Участники игры:\n{members}")


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    joined_users.clear()
    await update.message.reply_text("♻️ Список участников очищен.")


async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not joined_users:
        await update.message.reply_text("❌ Никто не присоединился к игре.")
        return

    # Если только один участник — он получает всё
    if len(joined_users) == 1:
        user = joined_users[0]
        geos = ", ".join(GEO_RULES.keys())
        await update.message.reply_text(f"{user} получает все гео: {geos}")
        return

    players = joined_users.copy()
    assigned = {player: [] for player in players}

    # === 1. Распределяем "fixed" GEO ===
    for geo, rule in GEO_RULES.items():
        if rule == "fixed" and players:
            player = players.pop(0)
            assigned[player].append(geo)

    # === 2. Распределяем "splittable" GEO ===
    for geo, rule in GEO_RULES.items():
        if rule == "splittable":
            parts = geo.split(", ")
            for part in parts:
                target = random.choice(list(assigned.keys()))
                assigned[target].append(part)

    # === 3. Распределяем "attachable" GEO ===
    for geo, rule in GEO_RULES.items():
        if rule == "attachable":
            target = random.choice(list(assigned.keys()))
            assigned[target].append(geo)

    # === Формируем сообщение ===
    lines = []
    for player, geos in assigned.items():
        if geos:
            lines.append(f"{player} — {', '.join(geos)}")
        else:
            lines.append(f"{player} — без назначения")

    await update.message.reply_text("\n".join(lines))


# === Основной запуск ===
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("join", join))
    app.add_handler(CommandHandler("list", list_members))
    app.add_handler(CommandHandler("roll", roll))
    app.add_handler(CommandHandler("reset", reset))

    print("🤖 Бот запущен. Ожидание команд...")
    app.run_polling()


if __name__ == "__main__":
    main()
