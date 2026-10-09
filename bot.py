

import os
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.environ["8389356778:AAEHvMBdeS5O0ge737eseLhJqL7VINeJHvM"]
ADMIN_ID = int(os.environ["8165015641"])

def init_db():
    with sqlite3.connect("entries.db") as db:
        db.execute(
            "CREATE TABLE IF NOT EXISTS entries (user_id INTEGER PRIMARY KEY, username TEXT)"
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("🎟️ မဲဖောက်ပွဲတွင် ပါဝင်ရန်", callback_data="join")
    ]]
    await update.message.reply_text(
        "🎉 NY DIAMOND Giveaway မှ ကြိုဆိုပါတယ်!\nမဲဖောက်ပွဲဝင်ရန် အောက်ကခလုတ်ကို နှိပ်ပါ။",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user = q.from_user
    username = f"@{user.username}" if user.username else user.full_name

    with sqlite3.connect("entries.db") as db:
        cur = db.execute(
            "INSERT OR IGNORE INTO entries VALUES (?, ?)",
            (user.id, username)
        )
        added = cur.rowcount == 1

    if added:
        await q.edit_message_text(f"✅ {username} စာရင်းသွင်းပြီးပါပြီ။")
        await context.bot.send_message(
            ADMIN_ID,
            f"🎟️ Giveaway စာရင်းအသစ်\nUsername: {username}\nID: {user.id}"
        )
    else:
        await q.edit_message_text("စာရင်းသွင်းပြီးသားပါ သားရီးရေ။")

async def entries(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    with sqlite3.connect("entries.db") as db:
        rows = db.execute(
            "SELECT username FROM entries ORDER BY rowid"
        ).fetchall()

    if not rows:
        await update.message.reply_text("စာရင်းမရှိသေးပါ။")
        return

    result = "🎟️ NY DIAMOND မဲဖောက်စာရင်း\n\n" + "\n".join(
        f"{i}. {row[0]}" for i, row in enumerate(rows, 1)
    )

    for i in range(0, len(result), 3500):
        await update.message.reply_text(result[i:i + 3500])

def main():
    init_db()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("entries", entries))
    app.add_handler(CallbackQueryHandler(join, pattern="^join$"))
    app.run_polling()

if __name__ == "__main__":
    main()
