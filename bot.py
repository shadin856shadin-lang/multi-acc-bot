import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

# আপনার দেওয়া টোকেন এবং অ্যাডমিন আইডি
API_TOKEN = '8809275642:AAFP4kuMiz-lNFQtPIBX4M1GneK0CUzTuck'
ADMIN_ID = 8262339619

logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    # ইউজার টেবিল
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY, 
                        username TEXT,
                        balance REAL DEFAULT 0.0)''')
    # স্টক টেবিল
    cursor.execute('''CREATE TABLE IF NOT EXISTS stock (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        category TEXT,
                        account_info TEXT, 
                        status TEXT DEFAULT 'available')''')
    conn.commit()
    conn.close()

init_db()

# --- Main Menu Keyboard ---
def get_main_menu():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("📧 জিমেইল শপ", callback_data="buy_gmail"),
        types.InlineKeyboardButton("💬 ওয়াটসঅ্যাপ শপ", callback_data="buy_whatsapp"),
        types.InlineKeyboardButton("✈️ টেলিগ্রাম শপ", callback_data="buy_telegram"),
        types.InlineKeyboardButton("💰 আমার ব্যালেন্স", callback_data="check_balance"),
        types.InlineKeyboardButton("➕ ব্যালেন্স অ্যাড", callback_data="add_balance"),
        types.InlineKeyboardButton("📊 স্টক স্ট্যাটাস", callback_data="stock_status"),
        types.InlineKeyboardButton("📞 কাস্টমার সাপোর্ট", callback_data="support")
    )
    return keyboard

# --- Back to Menu Keyboard ---
def get_back_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("🔙 মূল মেনুতে ফিরে যান", callback_data="back_to_main"))
    return keyboard

# --- Start Command ---
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "No Username"
    
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username, balance) VALUES (?, ?, ?)", (user_id, username, 0.0))
    conn.commit()
    conn.close()

    welcome_text = (
        f"🌟 **স্বাগতম, {message.from_user.first_name}!** 🌟\n\n"
        f"🛒 আমাদের প্রিমিয়াম অটোমেটেড অ্যাকাউন্ট শপে আপনাকে স্বাগতম।\n"
        f"নিরাপদে এবং দ্রুত জিমেইল, ওয়াটসঅ্যাপ ও টেলিগ্রাম অ্যাকাউন্ট কিনতে নিচের অপশনগুলো ব্যবহার করুন। 👇"
    )
    
    await message.answer(welcome_text, reply_markup=get_main_menu(), parse_mode="Markdown")

# --- Back to Main Menu Handler ---
@dp.callback_query_handler(text="back_to_main")
async def process_back(callback: types.CallbackQuery):
    welcome_text = (
        f"🌟 **মূল মেনু** 🌟\n\n"
        f"নিচের অপশনগুলো থেকে আপনার প্রয়োজনীয় সেবাটি বেছে নিন: 👇"
    )
    await callback.message.edit_text(welcome_text, reply_markup=get_main_menu(), parse_mode="Markdown")
    await callback.answer()

# --- Balance Check ---
@dp.callback_query_handler(text="check_balance")
async def process_balance(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    balance = row[0] if row else 0.0
    
    text = (
        f"💼 **ব্যালেন্স ইনফরমেশন**\n\n"
        f"👤 ইউজার আইডি: `{user_id}`\n"
        f"💰 বর্তমান ব্যালেন্স: **৳ {balance:.2f} BDT**"
    )
    await callback.message.edit_text(text, reply_markup=get_back_keyboard(), parse_mode="Markdown")
    await callback.answer()

# --- Stock Status Check ---
@dp.callback_query_handler(text="stock_status")
async def process_stock_status(callback: types.CallbackQuery):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM stock WHERE category = 'gmail' AND status = 'available'")
    gmail_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM stock WHERE category = 'whatsapp' AND status = 'available'")
    wa_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM stock WHERE category = 'telegram' AND status = 'available'")
    tg_count = cursor.fetchone()[0]
    conn.close()
    
    text = (
        f"📊 **বর্তমান লাইভ স্টক স্ট্যাটাস**\n\n"
        f"📧 জিমেইল স্টক: **{gmail_count} টি** (মূল্য: ৳২০)\n"
        f"💬 ওয়াটসঅ্যাপ স্টক: **{wa_count} টি** (মূল্য: ৳৫০)\n"
        f"✈️ টেলিগ্রাম স্টক: **{tg_count} টি** (মূল্য: ৳৪০)\n\n"
        f"✨ স্টক শেষ হওয়ার আগেই কিনে নিন!"
    )
    await callback.message.edit_text(text, reply_markup=get_back_keyboard(), parse_mode="Markdown")
    await callback.answer()

# --- Buy Categories (Gmail, WhatsApp, Telegram) ---
@dp.callback_query_handler(text=["buy_gmail", "buy_whatsapp", "buy_telegram"])
async def process_buy(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    
    if callback.data == "buy_gmail":
        category = "gmail"
        price = 20.0
        cat_name = "জিমেইল (Gmail)"
    elif callback.data == "buy_whatsapp":
        category = "whatsapp"
        price = 50.0
        cat_name = "ওয়াটসঅ্যাপ (WhatsApp)"
    else:
        category = "telegram"
        price = 40.0
        cat_name = "টেলিগ্রাম (Telegram)"
        
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    
    # ব্যালেন্স চেক
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    user_row = cursor.fetchone()
    user_balance = user_row[0] if user_row else 0.0
    
    if user_balance < price:
        await callback.answer(f"❌ পর্যাপ্ত ব্যালেন্স নেই! প্রয়োজন ৳{price}, আপনার আছে ৳{user_balance}", show_alert=True)
        conn.close()
        return

    # স্টক চেক
    cursor.execute("SELECT id, account_info FROM stock WHERE category = ? AND status = 'available' LIMIT 1", (category,))
    stock_row = cursor.fetchone()
    
    if not stock_row:
        await callback.answer(f"⚠️ দুঃখিত, বর্তমানে {cat_name} স্টকে নেই!", show_alert=True)
        conn.close()
        return
    
    stock_id, account_info = stock_row
    
    # ব্যালেন্স কাটা এবং স্টক আপডেট
    new_balance = user_balance - price
    cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))
    cursor.execute("UPDATE stock SET status = 'sold' WHERE id = ?", (stock_id,))
    conn.commit()
    conn.close()
    
    success_text = (
        f"🎉 **অর্ডার সফল হয়েছে!**\n\n"
        f"📦 ক্যাটাগরি: **{cat_name}**\n"
        f"🔑 বিবরণ:\n`{account_info}`\n\n"
        f"💡 নিরাপদে অ্যাকাউন্টটি লগইন করে পাসওয়ার্ড পরিবর্তন করে নিন। ধন্যবাদ!"
    )
    await callback.message.edit_text(success_text, reply_markup=get_back_keyboard(), parse_mode="Markdown")
    await callback.answer()

# --- Add Balance Info ---
@dp.callback_query_handler(text="add_balance")
async def process_add_balance(callback: types.CallbackQuery):
    text = (
        f"💳 **ব্যালেন্স রিচার্জ করার নিয়ম**\n\n"
        f"বিকাশ/নগদ/রকেট (Personal) নাম্বারে সেন্ড মানি করুন:\n"
        f"📱 `01XXXXXXXXX`\n\n"
        f"টাকা পাঠিয়ে ট্রানজাকশন আইডি (TrxID) সহ স্ক্রিনশট সরাসরি অ্যাডমিনকে পাঠান:\n"
        f"👉 `@AdminUsername`"
    )
    await callback.message.edit_text(text, reply_markup=get_back_keyboard(), parse_mode="Markdown")
    await callback.answer()

# --- Support ---
@dp.callback_query_handler(text="support")
async def process_support(callback: types.CallbackQuery):
    text = (
        f"📞 **কাস্টমার সাপোর্ট**\n\n"
        f"বট ব্যবহার করতে কোনো সমস্যা হলে বা অ্যাকাউন্টে কোনো সমস্যা দেখা দিলে আমাদের সাথে যোগাযোগ করুন:\n\n"
        f"👤 সাপোর্ট আইডি: `@AdminUsername`\n"
        f"⏰ সময়: ২৪/৭ একটিভ।"
    )
    await callback.message.edit_text(text, reply_markup=get_back_keyboard(), parse_mode="Markdown")
    await callback.answer()

# --- Admin Add Stock Command ---
@dp.message_handler(commands=['addstk'])
async def save_stock_command(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.reply("❌ আপনার এই কমান্ডটি ব্যবহারের অনুমতি নেই!")
        return
        
    try:
        parts = message.text.split(maxsplit=2)
        if len(parts) < 3:
            await message.reply("❌ ভুল ফরম্যাট! সঠিক নিয়মে লিখুন:\n`/addstk [category] [account_info]`\nউদাহরণ: `/addstk gmail user@gmail.com:password`")
            return
            
        category = parts[1].lower()
        account_info = parts[2]
        
        if category not in ['gmail', 'whatsapp', 'telegram']:
            await message.reply("❌ ক্যাটাগরি শুধু `gmail`, `whatsapp` অথবা `telegram` হতে পারবে।")
            return
            
        conn = sqlite3.connect('bot_database.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO stock (category, account_info, status) VALUES (?, ?, 'available')", (category, account_info))
        conn.commit()
        conn.close()
        
        await message.reply(f"✅ সফলভাবে **{category.upper()}** ক্যাটাগরিতে নতুন স্টক যুক্ত করা হয়েছে!")
    except Exception as e:
        await message.reply(f"❌ ত্রুটি ঘটেছে: {str(e)}")

# --- Admin Add Balance Command (/addbal user_id amount) ---
@dp.message_handler(commands=['addbal'])
async def add_balance_command(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
        
    try:
        parts = message.text.split()
        if len(parts) < 3:
            await message.reply("❌ সঠিক ফরম্যাট: `/addbal [user_id] [amount]`")
            return
            
        target_user_id = int(parts[1])
        amount = float(parts[2])
        
        conn = sqlite3.connect('bot_database.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, target_user_id))
        conn.commit()
        conn.close()
        
        await message.reply(f"✅ সফলভাবে ইউজার `{target_user_id}` এর অ্যাকাউন্টে ৳{amount} BDT যোগ করা হয়েছে!")
        
        try:
            await bot.send_message(target_user_id, f"🎉 আপনার অ্যাকাউন্টে সফলভাবে **৳{amount} BDT** ব্যালেন্স অ্যাড করা হয়েছে!", parse_mode="Markdown")
        except:
            pass
            
    except Exception as e:
        await message.reply(f"❌ ত্রুটি: {str(e)}")

if __name__ == '__main__':
    print("✨ স্টাইলিশ এবং প্রফেশনাল বট সফলভাবে চালু হচ্ছে...")
    executor.start_polling(dp, skip_updates=True)
