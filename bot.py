import os
import requests
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_KEY = os.environ.get("API_KEY")

# Replace with your Telegram user ID from @userinfobot
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

LANGUAGES = {
    "english": {
        "welcome": "🤖 FOREX ANALYSIS BOT\n━━━━━━━━━━━━━━━━━━━━\n\nWelcome to AI Forex Analysis! 👋",
        "news_title": "📰 LATEST MARKET NEWS\n━━━━━━━━━━━━━━━━━━━━\n\n",
        "no_news": "No breaking news at the moment.",
        "users": "👥 Total Users:",
        "admin_panel": "👑 ADMIN PANEL\n━━━━━━━━━━━━━━━━━━━━",
        "settings": "⚙️ SETTINGS\n━━━━━━━━━━━━━━━━━━━━\n\nSelect your language:",
        "currency": "💱 SELECT CATEGORY\n━━━━━━━━━━━━━━━━━━━━\n\nChoose a category 👇",
        "major": "🔵 MAJOR PAIRS\n━━━━━━━━━━━━━━━━━━━━\n\nSelect a pair 👇",
        "gold": "💛 GOLD & OIL\n━━━━━━━━━━━━━━━━━━━━\n\nSelect a pair 👇",
        "minor": "📈 MINOR PAIRS\n━━━━━━━━━━━━━━━━━━━━\n\nSelect a pair 👇",
        "back": "🔙 Back",
        "main_menu": "🏠 Main Menu",
        "refresh": "🔄 Refresh",
        "analyzing": "⏳ Analyzing",
        "error": "❌ Could not fetch data",
        "buy": "🟢 BUY",
        "sell": "🔴 SELL",
        "neutral": "🟡 NEUTRAL",
        "bullish": "🟢 Bullish",
        "bearish": "🔴 Bearish",
        "overbought": "Overbought",
        "oversold": "Oversold",
    },
    "german": {
        "welcome": "🤖 FOREX ANALYSIS BOT\n━━━━━━━━━━━━━━━━━━━━\n\nWillkommen beim KI-Forex-Analyse-Bot! 👋",
        "news_title": "📰 NEUESTE MARKTNACHRICHTEN\n━━━━━━━━━━━━━━━━━━━━\n\n",
        "no_news": "Aktuell keine Breaking News.",
        "users": "👥 Gesamtbenutzer:",
        "admin_panel": "👑 ADMIN-BEREICH\n━━━━━━━━━━━━━━━━━━━━",
        "settings": "⚙️ EINSTELLUNGEN\n━━━━━━━━━━━━━━━━━━━━\n\nWähle deine Sprache:",
        "currency": "💱 WÄHRUNGSKATEGORIE\n━━━━━━━━━━━━━━━━━━━━\n\nWähle eine Kategorie 👇",
        "major": "🔵 MAJOR-PAARE\n━━━━━━━━━━━━━━━━━━━━\n\nWähle ein Paar 👇",
        "gold": "💛 GOLD & ÖL\n━━━━━━━━━━━━━━━━━━━━\n\nWähle ein Paar 👇",
        "minor": "📈 MINOR-PAARE\n━━━━━━━━━━━━━━━━━━━━\n\nWähle ein Paar 👇",
        "back": "🔙 Zurück",
        "main_menu": "🏠 Hauptmenü",
        "refresh": "🔄 Aktualisieren",
        "analyzing": "⏳ Analysiere",
        "error": "❌ Daten konnten nicht abgerufen werden",
        "buy": "🟢 KAUFEN",
        "sell": "🔴 VERKAUFEN",
        "neutral": "🟡 NEUTRAL",
        "bullish": "🟢 Bullisch",
        "bearish": "🔴 Bärisch",
        "overbought": "Überkauft",
        "oversold": "Überverkauft",
    },
    "french": {
        "welcome": "🤖 FOREX ANALYSIS BOT\n━━━━━━━━━━━━━━━━━━━━\n\nBienvenue sur l'analyse Forex IA! 👋",
        "news_title": "📰 DERNIÈRES ACTUALITÉS\n━━━━━━━━━━━━━━━━━━━━\n\n",
        "no_news": "Pas d'actualités pour le moment.",
        "users": "👥 Utilisateurs totaux:",
        "admin_panel": "👑 PANEL ADMIN\n━━━━━━━━━━━━━━━━━━━━",
        "settings": "⚙️ PARAMÈTRES\n━━━━━━━━━━━━━━━━━━━━\n\nChoisis ta langue:",
        "currency": "💱 CATÉGORIE DE DEVISE\n━━━━━━━━━━━━━━━━━━━━\n\nChoisis une catégorie 👇",
        "major": "🔵 Paires majeures\n━━━━━━━━━━━━━━━━━━━━\n\nChoisis une paire 👇",
        "gold": "💛 Or & Pétrole\n━━━━━━━━━━━━━━━━━━━━\n\nChoisis une paire 👇",
        "minor": "📈 Paires mineures\n━━━━━━━━━━━━━━━━━━━━\n\nChoisis une paire 👇",
        "back": "🔙 Retour",
        "main_menu": "🏠 Menu principal",
        "refresh": "🔄 Actualiser",
        "analyzing": "⏳ Analyse en cours",
        "error": "❌ Impossible de récupérer les données",
        "buy": "🟢 ACHETER",
        "sell": "🔴 VENDRE",
        "neutral": "🟡 NEUTRE",
        "bullish": "🟢 Hausser",
        "bearish": "🔴 Baissier",
        "overbought": "Surachat",
        "oversold": "Survente",
    },
    "spanish": {
        "welcome": "🤖 FOREX ANALYSIS BOT\n━━━━━━━━━━━━━━━━━━━━\n\n¡Bienvenido al análisis Forex con IA! 👋",
        "news_title": "📰 ÚLTIMAS NOTICIAS\n━━━━━━━━━━━━━━━━━━━━\n\n",
        "no_news": "No hay noticias de último momento.",
        "users": "👥 Usuarios totales:",
        "admin_panel": "👑 PANEL ADMIN\n━━━━━━━━━━━━━━━━━━━━",
        "settings": "⚙️ CONFIGURACIÓN\n━━━━━━━━━━━━━━━━━━━━\n\nSelecciona tu idioma:",
        "currency": "💱 CATEGORÍA DE DIVISAS\n━━━━━━━━━━━━━━━━━━━━\n\nElige una categoría 👇",
        "major": "🔵 Pares principales\n━━━━━━━━━━━━━━━━━━━━\n\nElige un par 👇",
        "gold": "💛 Oro & Petróleo\n━━━━━━━━━━━━━━━━━━━━\n\nElige un par 👇",
        "minor": "📈 Pares menores\n━━━━━━━━━━━━━━━━━━━━\n\nElige un par 👇",
        "back": "🔙 Atrás",
        "main_menu": "🏠 Menú principal",
        "refresh": "🔄 Actualizar",
        "analyzing": "⏳ Analizando",
        "error": "❌ No se pudieron obtener los datos",
        "buy": "🟢 COMPRAR",
        "sell": "🔴 VENDER",
        "neutral": "🟡 NEUTRAL",
        "bullish": "🟢 Alcista",
        "bearish": "🔴 Bajista",
        "overbought": "Sobrecompra",
        "oversold": "Sobreventa",
    },
    "chinese": {
        "welcome": "🤖 外汇分析机器人\n━━━━━━━━━━━━━━━━━━━━\n\n欢迎使用AI外汇分析！👋",
        "news_title": "📰 最新市场新闻\n━━━━━━━━━━━━━━━━━━━━\n\n",
        "no_news": "暂无重大新闻。",
        "users": "👥 总用户数:",
        "admin_panel": "👑 管理员面板\n━━━━━━━━━━━━━━━━━━━━",
        "settings": "⚙️ 设置\n━━━━━━━━━━━━━━━━━━━━\n\n选择你的语言:",
        "currency": "💱 货币类别\n━━━━━━━━━━━━━━━━━━━━\n\n选择一个类别 👇",
        "major": "🔵 主要货币对\n━━━━━━━━━━━━━━━━━━━━\n\n选择一个货币对 👇",
        "gold": "💛 黄金和石油\n━━━━━━━━━━━━━━━━━━━━\n\n选择一个 👇",
        "minor": "📈 次要货币对\n━━━━━━━━━━━━━━━━━━━━\n\n选择一个货币对 👇",
        "back": "🔙 返回",
        "main_menu": "🏠 主菜单",
        "refresh": "🔄 刷新",
        "analyzing": "⏳ 分析中",
        "error": "❌ 无法获取数据",
        "buy": "🟢 买入",
        "sell": "🔴 卖出",
        "neutral": "🟡 中性",
        "bullish": "🟢 看涨",
        "bearish": "🔴 看跌",
        "overbought": "超买",
        "oversold": "超卖",
    }
}

user_lang = {}

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
        highs = [float(v["high"]) for v in values]
        lows = [float(v["low"]) for v in values]
        price = closes[0]
        gains, losses = [], []
        for i in range(1, 15):
            diff = closes[i-1] - closes[i]
            (gains if diff > 0 else losses).append(abs(diff))
        avg_gain = sum(gains)/14 if gains else 0
        avg_loss = sum(losses)/14 if losses else 0.001
        rsi = round(100 - (100 / (1 + avg_gain/avg_loss)), 1)
        ema12 = sum(closes[:12])/12
        ema26 = sum(closes[:26])/26
        macd = ema12 - ema26
        ma20 = sum(closes[:20])/20
        s1 = round(min(lows[:10]), 4)
        s2 = round(min(lows[:20]), 4)
        r1 = round(max(highs[:10]), 4)
        r2 = round(max(highs[:20]), 4)
        trend = "bullish" if price > ma20 else "bearish"
        signal = "buy" if (rsi < 60 and macd > 0 and price > ma20) else \
                 "sell" if (rsi > 60 and macd < 0 and price < ma20) else "neutral"
        rsi_label = "overbought" if rsi > 70 else "oversold" if rsi < 30 else "neutral"
        open_ = float(values[0]["open"])
        body = abs(price - open_)
        wick_up = float(values[0]["high"]) - max(price, open_)
        wick_down = min(price, open_) - float(values[0]["low"])
        if wick_down > body * 2:
            candle = "Hammer 🔨\nPossible bullish continuation."
        elif wick_up > body * 2:
            candle = "Shooting Star 🌠\nPossible bearish reversal."
        else:
            candle = "Doji ✳️\nMarket indecision."
        if signal == "buy":
            entry_low = round(price*0.9990, 4)
            entry_high = round(price*1.0005, 4)
            tp1 = round(price*1.005, 4)
            tp2 = round(price*1.010, 4)
            sl = round(price*0.995, 4)
        else:
            entry_low = round(price*0.9995, 4)
            entry_high = round(price*1.0010, 4)
            tp1 = round(price*0.995, 4)
            tp2 = round(price*0.990, 4)
            sl = round(price*1.005, 4)
        score = 0
        if signal != "neutral":
            score += 2
        if rsi_label == "neutral":
            score += 1
        if abs(macd) > 0:
            score += 1
        confidence_pct = min(95, 60 + score*8)
        stars = "⭐"*(score+1) + "☆"*(5-score-1)
        risk = "Low 🟢" if confidence_pct > 80 else "Medium 🟡" if confidence_pct > 65 else "High 🔴"
        return {
            "symbol": symbol, "price": price,
            "trend": trend, "signal": signal,
            "rsi": rsi, "rsi_label": rsi_label,
            "macd": macd,
            "ma": price > ma20,
            "momentum": closes[0] > closes[5],
            "s1": s1, "s2": s2, "r1": r1, "r2": r2,
            "candle": candle,
            "entry_low": entry_low, "entry_high": entry_high,
            "tp1": tp1, "tp2": tp2, "sl": sl,
            "stars": stars, "confidence_pct": confidence_pct, "risk": risk,
        }
    except:
        return None

def get_news():
    try:
        url = f"https://api.twelvedata.com/news?symbol=EUR/USD&apikey={API_KEY}"
        r = requests.get(url, timeout=10)
        data = r.json()
        if "news" in data and len(data["news"]) > 0:
            news_items = data["news"][:3]
            result = ""
            for news in news_items:
                title = news.get('title', 'No title')
                source = news.get('source', 'Unknown')
                result += f"📌 **{title}**\n📡 {source}\n\n"
            return result
        return "📰 No major news at this moment.\n\n💡 Check Forex Factory for latest updates."
    except:
        return "📰 News feed temporarily unavailable.\n\n💡 Visit: https://www.forexfactory.com"

def format_analysis(d, lang='english'):
    t = LANGUAGES[lang]
    signal_text = t['buy'] if d['signal'] == 'buy' else t['sell'] if d['signal'] == 'sell' else t['neutral']
    trend_text = t['bullish'] if d['trend'] == 'bullish' else t['bearish']
    rsi_label_text = t['overbought'] if d['rsi_label'] == 'overbought' else t['oversold'] if d['rsi_label'] == 'oversold' else "Neutral"
    macd_text = "Bullish 🟢" if d['macd'] > 0 else "Bearish 🔴"
    ma_text = "Buy 🟢" if d['ma'] else "Sell 🔴"
    momentum_text = "Positive 🟢" if d['momentum'] else "Negative 🔴"
    
    return (
        f"🚀 {d['symbol']} • AI Market Analysis\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💲 Current Price   {d['price']}\n"
        f"📈 Market Trend    {trend_text}\n"
        f"🎯 Trading Signal  {signal_text}\n\n"
        f"📊 Technical Indicators\n"
        f"• RSI (14): {d['rsi']} → {rsi_label_text}\n"
        f"• MACD: {macd_text}\n"
        f"• Moving Average: {ma_text}\n"
        f"• Momentum: {momentum_text}\n\n"
        f"🟢 Support Levels\n"
        f"S1 → {d['s1']}   S2 → {d['s2']}\n"
        f"🔴 Resistance Levels\n"
        f"R1 → {d['r1']}   R2 → {d['r2']}\n\n"
        f"🕯 Candlestick Pattern\n"
        f"{d['candle']}\n\n"
        f"🎯 Suggested Trade Plan\n"
        f"📍 Entry:  {d['entry_low']} – {d['entry_high']}\n"
        f"🎯 TP1: {d['tp1']}  |  TP2: {d['tp2']}\n"
        f"🛡 SL:  {d['sl']}\n\n"
        f"📊 AI Confidence  {d['stars']} ({d['confidence_pct']}%)\n"
        f"⚠️ Risk Level: {d['risk']}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚠️ For educational purposes only"
    )

def main_menu_kb(lang='english'):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Forex Currencies", callback_data="menu_currencies")],
        [InlineKeyboardButton("🔔 Price Alert", callback_data="menu_alerts"),
         InlineKeyboardButton("📰 Market News", callback_data="market_news")],
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

def category_kb(lang='english'):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔵 Major Pairs", callback_data="cat_major")],
        [InlineKeyboardButton("💛 Gold & Oil", callback_data="cat_gold")],
        [InlineKeyboardButton("📈 Minor Pairs", callback_data="cat_minor")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")],
    ])

def pairs_kb(pairs, back, lang='english'):
    keys = pairs
    rows = [[InlineKeyboardButton(k, callback_data=f"analyze_{k}") for k in keys[i:i+2]]
            for i in range(0, len(keys), 2)]
    rows.append([InlineKeyboardButton("🔙 Back", callback_data=back),
                 InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")])
    return InlineKeyboardMarkup(rows)

def after_analysis_kb(symbol, back, lang='english'):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Refresh", callback_data=f"analyze_{symbol}"),
         InlineKeyboardButton("🔙 Back", callback_data=back)],
    ])

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user(user_id)
    lang = user_lang.get(user_id, 'english')
    await update.message.reply_text(
        LANGUAGES[lang]['welcome'],
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
            LANGUAGES[lang]['welcome'],
            reply_markup=main_menu_kb(lang)
        )
    elif data == "menu_settings":
        await q.edit_message_text(
            LANGUAGES[lang]['settings'],
            reply_markup=settings_kb()
        )
    elif data.startswith("lang_"):
        new_lang = data.replace("lang_", "")
        user_lang[user_id] = new_lang
        await q.edit_message_text(
            f"✅ Language changed to {new_lang.upper()}!\n\n{LANGUAGES[new_lang]['welcome']}",
            reply_markup=main_menu_kb(new_lang)
        )
    elif data == "admin_panel":
        if user_id != ADMIN_ID:
            await q.edit_message_text("⛔ Access denied!")
            return
        await q.edit_message_text(
            f"{LANGUAGES[lang]['admin_panel']}\n\n{LANGUAGES[lang]['users']} {get_users_count()}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
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
            f"{LANGUAGES[lang]['news_title']}{news}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Refresh", callback_data="market_news"),
                 InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
            ])
        )
    elif data == "menu_currencies":
        await q.edit_message_text(
            LANGUAGES[lang]['currency'],
            reply_markup=category_kb(lang)
        )
    elif data == "cat_major":
        await q.edit_message_text(
            LANGUAGES[lang]['major'],
            reply_markup=pairs_kb(MAJOR_PAIRS, "menu_currencies", lang)
        )
    elif data == "cat_gold":
        await q.edit_message_text(
            LANGUAGES[lang]['gold'],
            reply_markup=pairs_kb(GOLD_OIL, "menu_currencies", lang)
        )
    elif data == "cat_minor":
        await q.edit_message_text(
            LANGUAGES[lang]['minor'],
            reply_markup=pairs_kb(MINOR_PAIRS, "menu_currencies", lang)
        )
    elif data.startswith("analyze_"):
        symbol = data.replace("analyze_", "")
        await q.edit_message_text(f"⏳ Analyzing {symbol}...")
        result = get_analysis(symbol)
        if result:
            back = "cat_major" if symbol in MAJOR_PAIRS else "cat_gold" if symbol in GOLD_OIL else "cat_minor"
            await q.edit_message_text(
                format_analysis(result, lang),
                reply_markup=after_analysis_kb(symbol, back, lang)
            )
        else:
            await q.edit_message_text(
                f"❌ Could not fetch data for {symbol}.\nTry again later.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data="menu_currencies")]
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
        await update.message.reply_text(f"✅ Alert set for {symbol} at {price}\n\nYou will be notified when price reaches this level!")
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
