from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
# === Конфигурация ===
TOKEN = "8450971744:AAEyHw6T6de18xodzn9J5gqsQwyh8kfc4fI"  # ← вставь токен своего бота
# === Глобальные переменные ===
joined_users = []

# Гео и их правила
GEO_POSITIONS = {
    "NPR": {"split": True, "can_attach": True},
    "BDT": {"split": True, "can_attach": True},
    "Асана, переключения, Рабочие, Контакты": {"split": False, "can_attach": True},
    "СНГ, LKR": {"split": False, "can_attach": True},
    "EGP, MAD": {"split": True, "can_attach": True},
    "PKR": {"split": True, "can_attach": True},
}

# === Команды ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎰 Привет! Я бот для распределения GEO по смене.\n"
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

    users = joined_users.copy()
    geos = list(GEO_POSITIONS.keys())
    assigned = {}

    # Если участников меньше, чем гео
    if len(users) < len(geos):
        await update.message.reply_text("⚠️ Участников меньше, чем GEO. Применяю адаптивное распределение...")

        # Распределяем базовые позиции
        for user in users:
            if geos:
                geo = geos.pop(0)
                assigned[user] = [geo]
            else:
                assigned[user] = []

        # Оставшиеся гео добавляем по правилам
        for geo in geos:
            info = GEO_POSITIONS[geo]
            if info["split"]:
                # Присоединяем к случайному игроку
                target = random.choice(list(assigned.keys()))
                assigned[target].append(geo)
            else:
                # Ищем, куда можно безопасно прикрепить
                possible_targets = [
                    u for u in assigned if any(GEO_POSITIONS[g]["can_attach"] for g in assigned[u])
                ]
                if possible_targets:
                    target = random.choice(possible_targets)
                    assigned[target].append(geo)
                else:
                    # если никто не подходит — просто кому-то
                    assigned[random.choice(list(assigned.keys()))].append(geo)
    else:
        # Если участников достаточно — классическое распределение
        assigned = {user: [geo] for user, geo in zip(users, geos)}

    # Формируем ответ
    lines = []
    for user, geolist in assigned.items():
        lines.append(f"{user} {', '.join(geolist)}")

    await update.message.reply_text("\n".join(lines))

# === Основной запуск ===
def main():
    app = ApplicationBuilder().token("ТВОЙ_ТОКЕН_ОТ_BOTFATHER").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("join", join))
    app.add_handler(CommandHandler("list", list_members))
    app.add_handler(CommandHandler("roll", roll))
    app.add_handler(CommandHandler("reset", reset))

    app.run_polling()

if __name__ == "__main__":
    main()
