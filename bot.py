import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ------------------ НАСТРОЙКИ ------------------
BOT_TOKEN = "8450971744:AAEyHw6T6de18xodzn9J5gqsQwyh8kfc4fI"  # токен от @BotFather

# ------------------ ДАННЫЕ ------------------
joined_users = []  # список участников

GEO_RULES = {
    # attachable — если выпал, больше не получает других GEO
    "NPR": "attachable",
    "BDT": "attachable",
    "PKR": "attachable",

    # fixed — назначаются целиком как блок (не делятся)
    "Асана, переключения, Рабочие, Контакты": "fixed",
    "СНГ, LKR": "fixed",

    # splittable — можно делить на отдельные GEO при нехватке участников
    "EGP, MAD": "splittable",
}


# ------------------ ВСПОМОГАТЕЛЬНЫЕ ------------------

def expand_splittable(rules):
    """Делит только splittable GEO, остальные остаются как есть."""
    expanded = {}
    for key, val in rules.items():
        if val == "splittable":
            parts = [x.strip() for x in key.split(",")]
            for part in parts:
                expanded[part] = val
        else:
            expanded[key] = val
    return expanded


EXPANDED_RULES = expand_splittable(GEO_RULES)


# ------------------ КОМАНДЫ ------------------

async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавляет игрока в список участников."""
    global joined_users
    user = update.effective_user.first_name
    if user not in joined_users:
        joined_users.append(user)
        await update.message.reply_text(f"✅ {user} присоединился к игре!")
    else:
        await update.message.reply_text(f"⚠️ {user}, ты уже в списке.")


async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает список подписавшихся участников."""
    global joined_users
    if not joined_users:
        await update.message.reply_text("📭 Никто ещё не присоединился.")
        return

    lines = [f"👥 *Список участников:*"]
    for i, user in enumerate(joined_users, 1):
        lines.append(f"{i}. {user}")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Очищает список участников."""
    global joined_users
    joined_users.clear()
    await update.message.reply_text("🔄 Список участников сброшен.")


async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Распределяет GEO между участниками."""
    global joined_users

    if not joined_users:
        await update.message.reply_text("❌ Никто не присоединился к игре.")
        return

    users = joined_users.copy()
    random.shuffle(users)

    assigned = {u: [] for u in users}
    locked = set()  # кто больше не получает GEO

    # --- Этап 1: splittable ---
    splittable_keys = [k for k, v in EXPANDED_RULES.items() if v == "splittable"]
    random.shuffle(splittable_keys)

    for geo in splittable_keys:
        target = min(assigned, key=lambda u: len(assigned[u]))
        assigned[target].append(geo)

    # --- Этап 2: fixed и attachable ---
    fixed_attachable = [(k, v) for k, v in GEO_RULES.items() if v in ("fixed", "attachable")]
    random.shuffle(fixed_attachable)

    for geo, gtype in fixed_attachable:
        available = [u for u in users if u not in locked]
        if not available:
            available = users.copy()

        target = min(available, key=lambda u: len(assigned[u]))
        assigned[target].append(geo)

        if len(fixed_attachable) <= len(users):
            locked.add(target)

    # --- Этап 3: все должны получить хотя бы одно GEO ---
    unassigned = [u for u in users if not assigned[u]]
    all_geos = list(EXPANDED_RULES.keys()) + list(GEO_RULES.keys())
    used_geos = [geo for geos in assigned.values() for geo in geos]
    leftovers = [g for g in all_geos if g not in used_geos]

    for user in unassigned:
        if leftovers:
            assigned[user].append(leftovers.pop())
        else:
            random_user = random.choice(users)
            assigned[user].append(f"{random_user}'s GEO (shared)")

    # --- Вывод результата ---
    lines = []
    for user, geolist in assigned.items():
        lines.append(f"{user} — {', '.join(geolist)}")

    lines.append("\n⚖️ Распределение завершено — все получили GEO!")
    await update.message.reply_text("\n".join(lines))


# ------------------ ИНИЦИАЛИЗАЦИЯ БОТА ------------------

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("join", join))
    app.add_handler(CommandHandler("list", list_users))
    app.add_handler(CommandHandler("roll", roll))
    app.add_handler(CommandHandler("reset", reset))

    print("🤖 Бот запущен. Слава Омниссии!")
    app.run_polling()


if __name__ == "__main__":
    main()
