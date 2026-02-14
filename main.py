import logging
import sqlite3
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Update
)

from config import BOT_TOKEN, OWNER_ID

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ConversationHandler
)

# ================= CONFIG =================

BOT_TZ = ZoneInfo("Asia/Kolkata")   # ⭐ Timezone Safe

ROLES_FILE = "roles.json"
DB_FILE = "schedule.db"

# ================= LOGGING =================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================= DATABASE =================

conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS schedules(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    datetime TEXT,
    role TEXT,
    created_by INTEGER
)
""")
conn.commit()

# ================= ROLE SYSTEM =================

def load_roles():
    try:
        with open(ROLES_FILE) as f:
            return json.load(f)
    except:
        roles = {"admins": [], "members": []}
        save_roles(roles)
        return roles

def save_roles(data):
    with open(ROLES_FILE, "w") as f:
        json.dump(data, f)

def get_role(uid):
    roles = load_roles()

    if uid == OWNER_ID:
        return "owner"
    if uid in roles["admins"]:
        return "admin"
    if uid in roles["members"]:
        return "member"
    return "guest"

# ================= REMINDER SYSTEM =================

async def send_reminder(context):
    job = context.job.data

    await context.bot.send_message(
        job["chat_id"],
        f"{job['msg']}\n\n📌 *{job['title']}*",
        parse_mode="Markdown"
    )


def schedule_reminders(context, title, event_dt, chat_id):

    now = datetime.now(BOT_TZ)
    diff = event_dt - now

    reminders = []

    # ⭐ Smart Dynamic Reminders
    if diff > timedelta(hours=2):
        reminders.append(("⏰ 1 Hour Remaining", timedelta(hours=1)))

    if diff > timedelta(minutes=30):
        reminders.append(("⏰ 30 Minutes Remaining", timedelta(minutes=30)))

    if diff > timedelta(minutes=10):
        reminders.append(("⏰ 10 Minutes Remaining", timedelta(minutes=10)))

    # Always include these
    reminders.append(("⚡ 1 Minute Remaining", timedelta(minutes=1)))
    reminders.append(("🚀 Event Started!", timedelta(seconds=0)))

    for text, delta in reminders:

        remind_time = event_dt - delta

        if remind_time > now:
            context.job_queue.run_once(
                send_reminder,
                when=remind_time,
                data={
                    "chat_id": chat_id,
                    "title": title,
                    "msg": text
                }
            )

# ================= DASHBOARD =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    role = get_role(user.id)

    if role == "guest":
        return await update.message.reply_text("❌ Access denied.")

    keyboard = [
        [InlineKeyboardButton("➕ Add Schedule", callback_data="add_schedule")],
        [InlineKeyboardButton("📅 View Schedules", callback_data="view_schedule")],
        [InlineKeyboardButton("❓ Help Center", callback_data="help")]
    ]

    if role == "owner":
        keyboard.append([
            InlineKeyboardButton("👤 Add Admin", callback_data="add_admin"),
            InlineKeyboardButton("👥 Add Member", callback_data="add_member")
        ])

    elif role == "admin":
        keyboard.append([
            InlineKeyboardButton("👥 Add Member", callback_data="add_member")
        ])

    text = f"""
✨ *Welcome {user.first_name}!*

👑 *Role:* {role.title()}

━━━━━━━━━━━━━━━━━
📌 Manage your schedules easily  
⚡ Use buttons below to navigate  
━━━━━━━━━━━━━━━━━
"""

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= HELP =================

async def help_cmd(update, context):

    await update.effective_message.reply_text("""
📘 *Command Guide*

🧩 /addschedule → Quick entry  
📊 /viewschedule → Show schedules  
👤 /addadmin USER_ID → Owner only  
👥 /addmember USER_ID → Admin+  

✨ Tip:
You can also use dashboard buttons!
""", parse_mode="Markdown")

# ================= VIEW =================

async def view_schedule(update, context):

    cursor.execute("SELECT title, datetime, role FROM schedules")
    rows = cursor.fetchall()

    if not rows:
        return await update.effective_message.reply_text("📭 No schedules saved yet.")

    text = "📅 *Your Scheduled Events*\n\n"

    for title, dt, role in rows:
        text += f"🔹 *{title}*\n🕒 {dt}\n🎯 {role}\n\n"

    await update.effective_message.reply_text(text, parse_mode="Markdown")

# ================= ROLE COMMANDS =================

async def add_admin(update, context):

    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("❌ Owner only")

    try:
        uid = int(context.args[0])
    except:
        return await update.message.reply_text("Usage: /addadmin USER_ID")

    roles = load_roles()
    if uid not in roles["admins"]:
        roles["admins"].append(uid)
        save_roles(roles)

    await update.message.reply_text("✅ Admin added successfully")


async def add_member(update, context):

    role = get_role(update.effective_user.id)

    if role not in ["owner", "admin"]:
        return await update.message.reply_text("❌ Not allowed")

    try:
        uid = int(context.args[0])
    except:
        return await update.message.reply_text("Usage: /addmember USER_ID")

    roles = load_roles()
    if uid not in roles["members"]:
        roles["members"].append(uid)
        save_roles(roles)

    await update.message.reply_text("✅ Member added successfully")

# ================= WIZARD =================

TITLE, DATE, TIME, TARGET, CONFIRM = range(5)

async def wizard_start(update, context):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text(
        "🧩 *Step 1 / 4*\n\n✏ Enter Event Name:",
        parse_mode="Markdown"
    )
    return TITLE


async def wizard_title(update, context):
    context.user_data["title"] = update.message.text

    await update.message.reply_text(
        "🧩 *Step 2 / 4*\n\n📅 Enter Date\nExample: 2026-02-12 or today or tomorrow",
        parse_mode="Markdown"
    )
    return DATE


async def wizard_date(update, context):

    text = update.message.text.lower().strip()
    now = datetime.now(BOT_TZ)

    if text == "today":
        date = now.date()

    elif text == "tomorrow":
        date = (now + timedelta(days=1)).date()

    else:
        try:
            date = datetime.strptime(text, "%Y-%m-%d").date()
        except:
            await update.message.reply_text("❌ Invalid date format.")
            return DATE

    context.user_data["date"] = date.strftime("%Y-%m-%d")

    await update.message.reply_text(
        "🧩 *Step 3 / 4*\n\n⏰ Enter Time\nExample: 18:30",
        parse_mode="Markdown"
    )
    return TIME


async def wizard_time(update, context):

    context.user_data["time"] = update.message.text.strip()

    keyboard = [
        [InlineKeyboardButton("👑 Admin", callback_data="target_admin")],
        [InlineKeyboardButton("👥 Member", callback_data="target_member")]
    ]

    await update.message.reply_text(
        "🧩 *Step 4 / 4*\n\n🎯 Who should receive this?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return TARGET


async def wizard_target(update, context):

    query = update.callback_query
    await query.answer()

    target = query.data.split("_")[1]
    context.user_data["target"] = target

    title = context.user_data["title"]
    dt = f"{context.user_data['date']} {context.user_data['time']}"

    keyboard = [
        [InlineKeyboardButton("✅ Confirm", callback_data="confirm")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ]

    await query.message.reply_text(
        f"""
📋 *Confirm Schedule*

📌 {title}
🕒 {dt}
🎯 {target}
""",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return CONFIRM


async def wizard_confirm(update, context):

    query = update.callback_query
    await query.answer()

    if query.data == "cancel":
        await query.message.reply_text("❌ Schedule cancelled")
        return ConversationHandler.END

    title = context.user_data["title"]
    dt = f"{context.user_data['date']} {context.user_data['time']}"
    target = context.user_data["target"]

    cursor.execute(
        "INSERT INTO schedules(title, datetime, role, created_by) VALUES(?,?,?,?)",
        (title, dt, target, query.from_user.id)
    )
    conn.commit()

    # ⭐ Timezone safe datetime
    try:
        naive_dt = datetime.strptime(dt, "%Y-%m-%d %H:%M")
        event_dt = naive_dt.replace(tzinfo=BOT_TZ)

        schedule_reminders(context, title, event_dt, query.from_user.id)

    except Exception as e:
        logger.error(e)

    await query.message.reply_text("🎉 Schedule saved successfully!")

    return ConversationHandler.END

# ================= INLINE MENU =================

async def menu_callback(update, context):

    query = update.callback_query
    await query.answer()

    if query.data == "view_schedule":
        return await view_schedule(update, context)

    if query.data == "help":
        return await help_cmd(update, context)

    if query.data == "add_admin":
        await query.message.reply_text("Use /addadmin USER_ID")

    if query.data == "add_member":
        await query.message.reply_text("Use /addmember USER_ID")

# ================= MAIN =================

def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    wizard = ConversationHandler(
        entry_points=[CallbackQueryHandler(wizard_start, pattern="^add_schedule$")],
        states={
            TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, wizard_title)],
            DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, wizard_date)],
            TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, wizard_time)],
            TARGET: [CallbackQueryHandler(wizard_target, pattern="^target_")],
            CONFIRM: [CallbackQueryHandler(wizard_confirm, pattern="^(confirm|cancel)$")]
        },
        fallbacks=[],
        per_user=True
    )

    app.add_handler(wizard)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("viewschedule", view_schedule))
    app.add_handler(CommandHandler("addadmin", add_admin))
    app.add_handler(CommandHandler("addmember", add_member))

    app.add_handler(CallbackQueryHandler(menu_callback, pattern="^(view_schedule|help|add_admin|add_member)$"))

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
