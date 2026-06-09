import os
import requests
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_KEY = os.environ.get("API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO_NAME = os.environ.get("REPO_NAME", "individualh000-lab/forex-analysis-bot")

ADMIN_ID = 8872922261

def load_users():
    try:
        url = f"https://api.github.com/repos/{REPO_NAME}/contents/users.txt"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            import base64
            data = r.json()
            content = base64.b64decode(data["content"]).decode('utf-8')
            return content.splitlines()
    except:
        pass
    return []

def save_users(users):
    try:
        url = f"https://api.github.com/repos/{REPO_NAME}/contents/users.txt"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        content = "\n".join(users)
        content_b64 = content.encode('utf-8').decode('utf-8')
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            data = r.json()
            put_data = {"message": "Update users", "content": content_b64, "sha": data["sha"]}
            requests.put(url, headers=headers, json=put_data)
        else:
            put_data = {"message": "Create users", "content": content_b64}
            requests.put(url, headers=headers, json=put_data)
    except:
        pass

def add_user(user_id):
    users = load_users()
    if str(user_id) not in users:
        users.append(str(user_id))
        save_users(users)

def get_user_count():
    return len(load_users())

MAJOR_PAIRS = ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD", "USD/CAD", "NZD/USD"]
MINOR_PAIRS = ["EUR/GBP", "EUR/JPY", "GBP/JPY", "AUD/JPY"]
GOLD_OIL = ["XAU/USD", "XAG/USD", "WTI/USD"]

def get_analysis(symbol):
    try:
        url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1h&outputsize=50&apikey={API_KEY}"
        r = requests.get(url, timeout=10)
        data = r.json()
        if "values" not in data:
            return None
        values = data["values"]
        closes = [float(v["close"]) for v in values]
        price = closes[0]
        return {"symbol": symbol, "price": price}
    except:
        return None

def format_analysis(d):
    return f"🚀 {d['symbol']}\n━━━━━━━━━━━━━━━━━━━━\n\n💲 Current Price: {d['price']}\n\n⚠️ For educational purposes only"

async def start(update, ctx):
    add_user(update.effective_user.id)
    keyboard = [[InlineKeyboardButton("📊 Forex", callback_data="menu_currencies")]]
    await update.message.reply_text("🤖 FOREX BOT", reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update, ctx):
    q = update.callback_query
    await q.answer()
    data = q.data
    if data == "menu_currencies":
        kb = [[InlineKeyboardButton(p, callback_data=f"pair_{p}")] for p in MAJOR_PAIRS[:3]]
        await q.edit_message_text("Select pair:", reply_markup=InlineKeyboardMarkup(kb))
    elif data.startswith("pair_"):
        symbol = data.replace("pair_", "")
        result = get_analysis(symbol)
        if result:
            await q.edit_message_text(format_analysis(result))

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    print("✅ Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()	
