import os
import requests
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_KEY = os.environ.get("API_KEY")

# Replace with your Telegram user ID (get from @userinfobot)
ADMIN_ID = 8398420395

USERS_FILE = "users.txt"

def save_user(user_id):
    try:
        with open(USERS_FILE, "r") as f:
            users = f.read().splitlines()
        if str(user_id) not in users:
            with open(USERS_FILE, "a") as f:
                f.write(f"{user_id}\n")
    except:
        with open(USERS_FILE, "w") as f:
            f.write(f"{user_id}\n")

def get_users_count():
    try:
        with open(USERS_FILE, "r") as f:
            return len(f.read().splitlines())
    except:
        return 0

# Language translations
LANGUAGES = {
    "english": {
        "welcome": "🤖 FOREX ANALYSIS BOT\n━━━━━━━━━━━━━━━━━━━━\n\nWelcome to AI Forex Analysis! 👋",
        "news_title": "📰 LATEST MARKET NEWS\n━━━━━━━━━━━━━━━━━━━━\n\n",
        "no_news": "No breaking news at the moment.",
        "users": "👥 Total Users:",
        "admin_panel": "👑 ADMIN PANEL\n━━━━━━━━━━━━━━━━━━━━",
        "settings": "⚙️ SETTINGS\n━━━━━━━━━━━━━━━━━━━━\n\nSelect your language:",
        "currency": "💱 SELECT CATEGORY",
        "major": "🔵 MAJOR PAIRS",
        "gold": "💛 GOLD & OIL",
        "minor": "📈 MINOR PAIRS",
        "back": "🔙 Back",
        "main_menu": "🏠 Main Menu",
        "refresh": "🔄 Refresh",
        "analyzing": "⏳ Analyzing",
        "error": "❌ Could not fetch data",
    },
    "german": {
        "welcome": "🤖 FOREX ANALYSIS BOT\n━━━━━━━━━━━━━━━━━━━━\n\nWillkommen beim KI-Forex-Analyse-Bot! 👋",
        "news_title": "📰 NEUESTE MARKTNACHRICHTEN\n━━━━━━━━━━━━━━━━━━━━\n\n",
        "no_news": "Aktuell keine Breaking News.",
        "users": "👥 Gesamtbenutzer:",
        "admin_panel": "👑 ADMIN-BEREICH\n━━━━━━━━━━━━━━━━━━━━",
        "settings": "⚙️ EINSTELLUNGEN\n━━━━━━━━━━━━━━━━━━━━\n\nWähle deine Sprache:",
        "currency": "💱 WÄHRUNGSKATEGORIE",
        "major": "🔵 MAJOR-PAARE",
        "gold": "💛 GOLD & ÖL",
        "minor": "📈 MINOR-PAARE",
        "back": "🔙 Zurück",
        "main_menu": "🏠 Hauptmenü",
        "refresh": "🔄 Aktualisieren",
        "analyzing": "⏳ Analysiere",
        "error": "❌ Daten konnten nicht abgerufen werden",
    },
    "french": {
        "welcome": "🤖 FOREX ANALYSIS BOT\n━━━━━━━━━━━━━━━━━━━━\n\nBienvenue sur l'analyse Forex IA! 👋",
        "news_title": "📰 DERNIÈRES ACTUALITÉS\n━━━━━━━━━━━━━━━━━━━━\n\n",
        "no_news": "Pas d'actualités pour le moment.",
        "users": "👥 Utilisateurs totaux:",
        "admin_panel": "👑 PANEL ADMIN\n━━━━━━━━━━━━━━━━━━━━",
        "settings": "⚙️ PARAMÈTRES\n━━━━━━━━━━━━━━━━━━━━\n\nChoisis ta langue:",
        "currency": "💱 CATÉGORIE DE DEVISE",
        "major": "🔵 Paires majeures",
        "gold": "💛 Or & Pétrole",
        "minor": "📈 Paires mineures",
        "back": "🔙 Retour",
        "main_menu": "🏠 Menu principal",
        "refresh": "🔄 Actualiser",
        "analyzing": "⏳ Analyse en cours",
        "error": "❌ Impossible de récupérer les données",
    },
    "spanish": {
        "welcome": "🤖 FOREX ANALYSIS BOT\n━━━━━━━━━━━━━━━━━━━━\n\n¡Bienvenido al análisis Forex con IA! 👋",
        "news_title": "📰 ÚLTIMAS NOTICIAS\n━━━━━━━━━━━━━━━━━━━━\n\n",
        "no_news": "No hay noticias de último momento.",
        "users": "👥 Usuarios totales:",
        "admin_panel": "👑 PANEL ADMIN\n━━━━━━━━━━━━━━━━━━━━",
        "settings": "⚙️ CONFIGURACIÓN\n━━━━━━━━━━━━━━━━━━━━\n\nSelecciona tu idioma:",
        "currency": "💱 CATEGORÍA DE DIVISAS",
        "major": "🔵 Pares principales",
        "gold": "💛 Oro & Petróleo",
        "minor": "📈 Pares menores",
        "back": "🔙 Atrás",
        "main_menu": "🏠 Menú principal",
        "refresh": "🔄 Actualizar",
        "analyzing": "⏳ Analizando",
        "error": "❌ No se pudieron obtener los datos",
    },
    "chinese": {
        "welcome": "🤖 外汇分析机器人\n━━━━━━━━━━━━━━━━━━━━\n\n欢迎使用AI外汇分析！👋",
        "news_title": "📰 最新市场新闻\n━━━━━━━━━━━━━━━━━━━━\n\n",
        "no_news": "暂无重大新闻。",
        "users": "👥 总用户数:",
        "admin_panel": "👑 管理员面板\n━━━━━━━━━━━━━━━━━━━━",
        "settings": "⚙️ 设置\n━━━━━━━━━━━━━━━━━━━━\n\n选择你的语言:",
        "currency": "💱 货币类别",
        "major": "🔵 主要货币对",
        "gold": "💛 黄金和石油",
        "minor": "📈 次要货币对",
        "back": "🔙 返回",
        "main_menu": "🏠 主菜单",
        "refresh": "🔄 刷新",
        "analyzing": "⏳ 分析中",
        "error": "❌ 无法获取数据",
    }
}

# Store user language
user_lang = {}

MAJOR_PAIRS = ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD", "USD/CAD", "NZD/USD"]
MINOR_PAIRS = ["EUR/GBP", "EUR/JPY", "GBP/JPY", "AUD/JPY"]
GOLD_OIL = ["XAU/USD", "XAG/USD", "WTI/USD"]

def get_news():
    try:
        # Use free Forex News API
        url = "https://api.twelvedata.com/news?symbol=EUR/USD&apikey=" + API_KEY
        r = requests.get(url, timeout=10)
        data = r.json()
        
        if "news" in data and len(data["news"]) > 0:
            news_items = data["news"][:5]
            result = ""
            for news in news_items:
                title = news.get('title', 'No title')
                source = news.get('source', 'Unknown')
                result += f"📌 **{title}**\n📡 {source}\n\n"
            return result
        else:
            return "📰 No major news at this moment.\n\n💡 Check Forex Factory for latest updates."
    except:
        return "📰 News feed temporarily unavailable.\n\n💡 Visit: https://www.forexfactory.com"

def get_price(symbol):
    try:
        url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={API_KEY}"
        r = requests.get(url, timeout=10)
        data = r.json()
        return data.get('price', 'N/A')
    except:
        return 'N/A'

def get_text(key, lang='english'):
    return LANGUAGES.get(lang, LANGUAGES['english']).get(key, key)

def main_menu_kb(lang='english'):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Forex", callback_data="menu_currencies")],
        [InlineKeyboardButton("🔔 Alert", callback_data="menu_alerts"),
         InlineKeyboardButton("📰 News", callback_data="market_news")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings"),
         InlineKeyboardButton("👑 Admin", callback_data="admin_panel")],
    ])

def settings_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_english"),
         InlineKeyboardButton("🇩🇪 Deutsch", callback_data="lang_german")],
        [InlineKeyboardButton("🇫🇷 Français", callback_data="lang_french"),
         InlineKeyboardButton("🇪🇸 Español", callback_data="lang_spanish")],
        [InlineKeyboardButton("🇨🇳 中文", callback_data="lang_chinese")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")],
    ])

def admin_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 User Stats", callback_data="admin_stats")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")],
    ])

def category_kb(lang='english'):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔵 Major Pairs", callback_data="cat_major")],
        [InlineKeyboardButton("💛 Gold & Oil", callback_data="cat_gold")],
        [InlineKeyboardButton("📈 Minor Pairs", callback_data="cat_minor")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")],
    ])

def pairs_kb(pairs, back, lang='english'):
    rows = [[InlineKeyboardButton(p, callback_data=f"price_{p}")] for p in pairs]
    rows.append([InlineKeyboardButton(get_text('back', lang), callback_data=back),
                 InlineKeyboardButton(get_text('main_menu', lang), callback_data="main_menu")])
    return InlineKeyboardMarkup(rows)

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user(user_id)
    lang = user_lang.get(user_id, 'english')
    await update.message.reply_text(
        get_text('welcome', lang),
        reply_markup=main_menu_kb(lang)
    )

async def button(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    user_id = update.effective_user.id
    lang = user_lang.get(user_id, 'english')

    if data == "main_menu":
        await q.edit_message_text(
            get_text('welcome', lang),
            reply_markup=main_menu_kb(lang)
        )
    elif data == "menu_settings":
        await q.edit_message_text(
            get_text('settings', lang),
            reply_markup=settings_kb()
        )
    elif data.startswith("lang_"):
        new_lang = data.replace("lang_", "")
        user_lang[user_id] = new_lang
        await q.edit_message_text(
            f"✅ Language changed to {new_lang.upper()}!\n\n{get_text('welcome', new_lang)}",
            reply_markup=main_menu_kb(new_lang)
        )
    elif data == "admin_panel":
        if user_id != ADMIN_ID:
            await q.edit_message_text("⛔ Access denied!", reply_markup=main_menu_kb(lang))
            return
        await q.edit_message_text(
            f"{get_text('admin_panel', lang)}\n\n{get_text('users', lang)} {get_users_count()}",
            reply_markup=admin_kb()
        )
    elif data == "admin_stats":
        if user_id != ADMIN_ID:
            await q.edit_message_text("⛔ Access denied!")
            return
        await q.edit_message_text(
            f"📊 Bot Statistics\n━━━━━━━━━━━━━━━━━━━━\n\n👥 Total Users: {get_users_count()}\n✅ Status: Active\n🌐 24/7 Online",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]
            ])
        )
    elif data == "menu_alerts":
        await q.edit_message_text(
            "🔔 Price Alert\n━━━━━━━━━━━━━━━━━━━━\n\nSend /setalert [SYMBOL] [PRICE]\n\nExample:\n/setalert EUR/USD 1.2000",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
            ])
        )
    elif data == "market_news":
        await q.edit_message_text("⏳ Fetching latest news...")
        news = get_news()
        await q.edit_message_text(
            f"{get_text('news_title', lang)}{news}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(get_text('refresh', lang), callback_data="market_news"),
                 InlineKeyboardButton(get_text('main_menu', lang), callback_data="main_menu")]
            ])
        )
    elif data == "menu_currencies":
        await q.edit_message_text(
            get_text('currency', lang),
            reply_markup=category_kb(lang)
        )
    elif data == "cat_major":
        await q.edit_message_text(
            get_text('major', lang),
            reply_markup=pairs_kb(MAJOR_PAIRS, "menu_currencies", lang)
        )
    elif data == "cat_gold":
        await q.edit_message_text(
            get_text('gold', lang),
            reply_markup=pairs_kb(GOLD_OIL, "menu_currencies", lang)
        )
    elif data == "cat_minor":
        await q.edit_message_text(
            get_text('minor', lang),
            reply_markup=pairs_kb(MINOR_PAIRS, "menu_currencies", lang)
        )
    elif data.startswith("price_"):
        symbol = data.replace("price_", "")
        await q.edit_message_text(f"⏳ Getting {symbol} price...")
        price = get_price(symbol)
        await q.edit_message_text(
            f"💱 {symbol}\n━━━━━━━━━━━━━━━━━━━━\n\n💰 Current Price: {price}\n\nPowered by Twelve Data",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Refresh", callback_data=f"price_{symbol}"),
                 InlineKeyboardButton("🔙 Back", callback_data="cat_major" if symbol in MAJOR_PAIRS else "cat_gold" if symbol in GOLD_OIL else "cat_minor")],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
            ])
        )

async def set_alert(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        args = ctx.args
        if len(args) < 2:
            await update.message.reply_text("⚠️ Usage: /setalert [SYMBOL] [PRICE]\nExample: /setalert EUR/USD 1.2000")
            return
        symbol = args[0].upper()
        price = float(args[1])
        await update.message.reply_text(f"✅ Alert set for {symbol} at {price}\n\nYou will be notified when price reaches this level!\n\n(Notification system coming soon)")
    except:
        await update.message.reply_text("❌ Invalid format. Use: /setalert EUR/USD 1.2000")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setalert", set_alert))
    app.add_handler(CallbackQueryHandler(button))
    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
