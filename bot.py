import logging
import os
import sqlite3
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# আপনার দেওয়া টোকেন এবং অ্যাডমিন আইডি
API_TOKEN = "8809275642:AAFP4kuMiz-lNFQtPIBX4M1GneK0CUzTuck"
ADMIN_ID = 8262339619

# লগিং সেটআপ
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# --- Database Setup ---
def init_db():
  conn = sqlite3.connect("bot_database.db")
  cursor = conn.cursor()
  # ইউজার টেবিল
  cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY, 
                        username TEXT,
                        balance REAL DEFAULT 0.0)""")
  # স্টক টেবিল
  cursor.execute("""CREATE TABLE IF NOT EXISTS stock (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        category TEXT,
                        account_info TEXT, 
                        status TEXT DEFAULT 'available')""")
  conn.commit()
  conn.close()


init_db()


# --- Main Menu Keyboard ---
def get_main_menu():
  keyboard = [
      [
          InlineKeyboardButton("📧 জিমেইল শপ", callback_data="buy_gmail"),
          InlineKeyboardButton(
              "💬 ওয়াটসঅ্যাপ শপ", callback_data="buy_whatsapp"
          ),
      ],
      [
          InlineKeyboardButton("✈️ টেলিগ্রাম শপ", callback_data="buy_telegram"),
          InlineKeyboardButton("💰 আমার ব্যালেন্স", callback_data="check_balance"),
      ],
      [
          InlineKeyboardButton("➕ ব্যালেন্স অ্যাড", callback_data="add_balance"),
          InlineKeyboardButton("📊 স্টক স্ট্যাটাস", callback_data="stock_status"),
      ],
      [InlineKeyboardButton("📞 কাস্টমার সাপোর্ট", callback_data="support")],
  ]
  return InlineKeyboardMarkup(keyboard)


# --- Back to Menu Keyboard ---
def get_back_keyboard():
  keyboard = [
      [
          InlineKeyboardButton(
              "🔙 মূল মেনুতে ফিরে যান", callback_data="back_to_main"
          )
      ]
  ]
  return InlineKeyboardMarkup(keyboard)


# --- Start Command ---
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user = update.effective_user
  user_id = user.id
  username = user.username or "No Username"

  conn = sqlite3.connect("bot_database.db")
  cursor = conn.cursor()
  cursor.execute(
      "INSERT OR IGNORE INTO users (user_id, username, balance) VALUES (?, ?,"
      " ?)",
      (user_id, username, 0.0),
  )
  conn.commit()
  conn.close()

  welcome_text = (
      f"🌟 *স্বাগতম, {user.first_name}!* 🌟\n\n"
      "🛒 আমাদের প্রিমিয়াম অটোমেটেড অ্যাকাউন্ট শপে আপনাকে স্বাগতম।\n"
      "নিরাপদে এবং দ্রুত জিমেইল, ওয়াটসঅ্যাপ ও টেলিগ্রাম অ্যাকাউন্ট কিনতে নিচের"
      " অপশনগুলো ব্যবহার করুন। 👇"
  )

  await update.message.reply_text(
      welcome_text, reply_markup=get_main_menu(), parse_mode="Markdown"
  )


# --- Callback Query Handler ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
  query = update.callback_query
  await query.answer()
  data = query.data
  user_id = query.from_user.id

  if data == "back_to_main":
    welcome_text = (
        "🌟 *মূল মেনু* 🌟\n\nনিচের অপশনগুলো থেকে আপনার প্রয়োজনীয় সেবাটি বেছে"
        " নিন: 👇"
    )
    await query.edit_message_text(
        welcome_text, reply_markup=get_main_menu(), parse_mode="Markdown"
    )

  elif data == "check_balance":
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    balance = row[0] if row else 0.0
    text = (
        f"💼 *ব্যালেন্স ইনফরমেশন*\n\n👤 ইউজার আইডি: `{user_id}`\n💰 বর্তমান ব্যালেন্স:"
        f" *৳ {balance:.2f} BDT*"
    )
    await query.edit_message_text(
        text, reply_markup=get_back_keyboard(), parse_mode="Markdown"
    )

  elif data == "stock_status":
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM stock WHERE category = 'gmail' AND status ="
        " 'available'"
    )
    gmail_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM stock WHERE category = 'whatsapp' AND status ="
        " 'available'"
    )
    wa_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM stock WHERE category = 'telegram' AND status ="
        " 'available'"
    )
    tg_count = cursor.fetchone()[0]
    conn.close()

    text = (
        "📊 *বর্তমান লাইভ স্টক স্ট্যাটাস*\n\n"
        f"📧 জিমেইল স্টক: *{gmail_count} টি* (মূল্য: ৳২০)\n"
        f"💬 ওয়াটসঅ্যাপ স্টক: *{wa_count} টি* (মূল্য: ৳৫০)\n"
        f"✈️ টেলিগ্রাম স্টক: *{tg_count} টি* (মূল্য: ৳৪০)\n\n"
        "✨ স্টক শেষ হওয়ার আগেই কিনে নিন!"
    )
    await query.edit_message_text(
        text, reply_markup=get_back_keyboard(), parse_mode="Markdown"
    )

  elif data in ["buy_gmail", "buy_whatsapp", "buy_telegram"]:
    if data == "buy_gmail":
      category = "gmail"
      price = 20.0
      cat_name = "জিমেইল (Gmail)"
    elif data == "buy_whatsapp":
      category = "whatsapp"
      price = 50.0
      cat_name = "ওয়াটসঅ্যাপ (WhatsApp)"
    else:
      category = "telegram"
      price = 40.0
      cat_name = "টেলিগ্রাম (Telegram)"

    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    user_row = cursor.fetchone()
    user_balance = user_row[0] if user_row else 0.0

    if user_balance < price:
      await query.answer(
          f"❌ পর্যাপ্ত ব্যালেন্স নেই! প্রয়োজন ৳{price}, আপনার আছে ৳{user_balance}",
          show_alert=True,
      )
      conn.close()
      return

    cursor.execute(
        "SELECT id, account_info FROM stock WHERE category = ? AND status ="
        " 'available' LIMIT 1",
        (category,),
    )
    stock_row = cursor.fetchone()

    if not stock_row:
      await query.answer(
          f"⚠️ দুঃখিত, বর্তমানে {cat_name} স্টকে নেই!", show_alert=True
      )
      conn.close()
      return

    stock_id, account_info = stock_row

    new_balance = user_balance - price
    cursor.execute(
        "UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id)
    )
    cursor.execute(
        "UPDATE stock SET status = 'sold' WHERE id = ?", (stock_id,)
    )
    conn.commit()
    conn.close()

    success_text = (
        f"🎉 *অর্ডার সফল হয়েছে!*\n\n📦 ক্যাটাগরি: *{cat_name}*\n🔑 বিবরণ:\n`{account_info}`\n\n💡"
        " নিরাপদে অ্যাকাউন্টটি লগইন করে পাসওয়ার্ড পরিবর্তন করে নিন। ধন্যবাদ!"
    )
    await query.edit_message_text(
        success_text, reply_markup=get_back_keyboard(), parse_mode="Markdown"
    )

  elif data == "add_balance":
    text = (
        "💳 *ব্যালেন্স রিচার্জ করার নিয়ম*\n\nবিকাশ/নগদ/রকেট (Personal) নাম্বারে"
        " সেন্ড মানি করুন:\n📱 `01XXXXXXXXX`\n\nটাকা পাঠিয়ে ট্রানজাকশন আইডি"
        " (TrxID) সহ স্ক্রিনশট সরাসরি অ্যাডমিনকে পাঠান:\n👉 `@AdminUsername`"
    )
    await query.edit_message_text(
        text, reply_markup=get_back_keyboard(), parse_mode="Markdown"
    )

  elif data == "support":
    text = (
        "📞 *কাস্টমার সাপোর্ট*\n\nবট ব্যবহার করতে কোনো সমস্যা হলে বা অ্যাকাউন্টে"
        " কোনো সমস্যা দেখা দিলে আমাদের সাথে যোগাযোগ করুন:\n\n👤 সাপোর্ট আইডি:"
        " `@AdminUsername`\n⏰ সময়: ২৪/৭ একটিভ।"
    )
    await query.edit_message_text(
        text, reply_markup=get_back_keyboard(), parse_mode="Markdown"
    )


# --- Admin Add Stock Command (/addstk) ---
async def save_stock_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  if update.effective_user.id != ADMIN_ID:
    await update.message.reply_text("❌ আপনার এই কমান্ডটি ব্যবহারের অনুমতি নেই!")
    return

  try:
    args = context.args
    if len(args) < 2:
      await update.message.reply_text(
          "❌ ভুল ফরম্যাট! সঠিক নিয়মে লিখুন:\n`/addstk [category]"
          " [account_info]`\nউদাহরণ: `/addstk gmail user@gmail.com:password`",
          parse_mode="Markdown",
      )
      return

    category = args[0].lower()
    account_info = " ".join(args[1:])

    if category not in ["gmail", "whatsapp", "telegram"]:
      await update.message.reply_text(
          "❌ ক্যাটাগরি শুধু `gmail`, `whatsapp` অথবা `telegram` হতে পারবে।"
      )
      return

    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO stock (category, account_info, status) VALUES (?, ?,"
        " 'available')",
        (category, account_info),
    )
    conn.commit()
    conn.close()

    await update.message.reply_text(
        f"✅ সফলভাবে *{category.upper()}* ক্যাটাগরিতে নতুন স্টক যুক্ত করা হয়েছে!",
        parse_mode="Markdown",
    )
  except Exception as e:
    await update.message.reply_text(f"❌ ত্রুটি ঘটেছে: {str(e)}")


# --- Admin Add Balance Command (/addbal) ---
async def add_balance_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
  if update.effective_user.id != ADMIN_ID:
    return

  try:
    args = context.args
    if len(args) < 2:
      await update.message.reply_text(
          "❌ সঠিক ফরম্যাট: `/addbal [user_id] [amount]`", parse_mode="Markdown"
      )
      return

    target_user_id = int(args[0])
    amount = float(args[1])

    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET balance = balance + ? WHERE user_id = ?",
        (amount, target_user_id),
    )
    conn.commit()
    conn.close()

    await update.message.reply_text(
        f"✅ সফলভাবে ইউজার `{target_user_id}` এর অ্যাকাউন্টে ৳{amount} BDT যোগ"
        " করা হয়েছে!",
        parse_mode="Markdown",
    )

    try:
      await context.bot.send_message(
          target_user_id,
          f"🎉 আপনার অ্যাকাউন্টে সফলভাবে *৳{amount} BDT* ব্যালেন্স অ্যাড করা"
          " হয়েছে!",
          parse_mode="Markdown",
      )
    except:
      pass

  except Exception as e:
    await update.message.reply_text(f"❌ ত্রুটি: {str(e)}")


def main():
  # Render এনভায়রনমেন্ট বা সরাসরি টোকেন সেটআপ
  TOKEN = os.getenv("BOT_TOKEN", API_TOKEN)

  application = Application.builder().token(TOKEN).build()

  # হ্যান্ডলার রেজিস্টার করা
  application.add_handler(CommandHandler("start", cmd_start))
  application.add_handler(CommandHandler("addstk", save_stock_command))
  application.add_handler(CommandHandler("addbal", add_balance_command))
  application.add_handler(CallbackQueryHandler(button_handler))

  print("✨ স্টাইলিশ এবং প্রফেশনাল বট সফলভাবে চালু হচ্ছে...")
  application.run_polling()


if __name__ == "__main__":
  main()
