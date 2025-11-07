import random
from telegram import Update
from telegram.ext import ContextTypes

# Пример GEO_RULES
GEO_RULES = {
    "NPR": "attachable",
    "BDT": "attachable",
    "Асана, переключения, Рабочие, Контакты": "fixed",
    "СНГ, LKR": "fixed",
    "EGP, MAD": "splittable",
    "PKR": "attachable"
}

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not joined_users:
        await update.message.reply_text("❌ Никто не присоединился к игре.")
        return

    # Если один игрок — получает всё
    if len(joined_users) == 1:
        user = joined_users[0]
        all_geos = ", ".join(GEO_RULES.keys())
        await update.message.reply_text(f"{user} получает все гео: {all_geos}")
        return

    users = joined_users.copy()
    random.shuffle(users)

    geos = list(GEO_RULES.keys())
    random.shuffle(geos)

    assigned = {user: [] for user in users}

    # --- Этап 1: распределяем "fixed" GEO равномерно ---
    fixed_geos = [g for g, t in GEO_RULES.items() if t == "fixed"]
    for i, geo in enumerate(fixed_geos):
        target = users[i % len(users)]
        assigned[target].append(geo)

    # --- Этап 2: распределяем "attachable" GEO ---
    attachable_geos = [g for g, t in GEO_RULES.items() if t == "attachable"]
    for geo in attachable_geos:
        # Найдём у кого меньше всего GEO, чтобы баланс был ровным
        target = min(assigned, key=lambda u: len(assigned[u]))
        assigned[target].append(geo)

    # --- Этап 3: распределяем "splittable" GEO ---
    splittable_geos = [g for g, t in GEO_RULES.items() if t == "splittable"]
    for geo in splittable_geos:
        # Эти можно отдать нескольким игрокам, но равномерно
        targets = random.sample(users, k=min(len(users), 2))  # максимум двум
        for t in targets:
            assigned[t].append(geo + " (shared)")

    # --- Формируем вывод ---
    lines = []
    for user, geolist in assigned.items():
        if geolist:
            lines.append(f"{user} — {', '.join(geolist)}")
        else:
            lines.append(f"{user} — без назначения ❌")

    await update.message.reply_text("\n".join(lines))
