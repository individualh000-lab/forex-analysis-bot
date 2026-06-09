import os
import requests
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_KEY = os.environ.get("API_KEY")

ALERTS_FILE = "alerts.json"

def load_alerts():
    try:
        with open(ALERTS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_alerts(alerts):
    with open(ALERTS_FILE, "w") as f:
        json.dump(alerts, f)

MAJOR_PAIRS = {
    "EUR/USD": "EUR/USD",
    "GBP/USD": "GBP/USD",
    "USD/JPY": "USD/JPY",
    "USD/CHF": "USD/CHF",
    "AUD/USD": "AUD/USD",
    "USD/CAD": "USD/CAD",
    "NZD/USD": "NZD/USD",
}

MINOR_PAIRS = {
    "EUR/GBP": "EUR/GBP",
    "EUR/JPY": "EUR/JPY",
    "GBP/JPY": "GBP/JPY",
    "AUD/JPY": "AUD/JPY",
}

GOLD_OIL = {
    "XAU/USD": "XAU/USD",
    "XAG/USD": "XAG/USD",
    "WTI/USD": "WTI/USD",
}

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
        trend = "🟢 Bullish" if price > ma20 else "🔴 Bearish"
        signal = "🟢 BUY" if (rsi < 60 and macd > 0 and price > ma20) else \
                 "🔴 SELL" if (rsi > 60 and macd < 0 and price < ma20) else "🟡 NEUTRAL"
        rsi_label = "Overbought" if rsi > 70 else "Oversold" if rsi < 30 else "Neutral"
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
        if "BUY" in signal:
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
        if "BUY" in signal or "SELL" in signal:
            score += 2
        if rsi_label == "Neutral":
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
            "macd": "Bullish 🟢" if macd > 0 else "Bearish 🔴",
            "ma": "Buy 🟢" if price > ma20 else "Sell 🔴",
            "momentum": "Positive 🟢" if closes[0] > closes[5] else "Negative 🔴",
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
            news = data["news"][0]
            return f"📰 Latest News:\n\n{news.get('title', 'No title')}\n\n{news.get('summary', 'No summary')[:200]}..."
        return "📰 No important news found."
    except:
        return "📰 Unable to fetch news at this time."

def format_analysis(d):
    return (
        f"🚀 {d['symbol']} • AI Market Analysis\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💲 Current Price   {d['price']}\n"
        f"📈 Market Trend    {d['trend']}\n"
        f"🎯 Trading Signal  {d['signal']}\n\n"
        f"📊 Technical Indicators\n"
        f"• RSI (14): {d['rsi']} → {d['rsi_label']}\n"
        f"• MACD: {d['macd']}\n"
        f"• Moving Average: {d['ma']}\n"
        f"• Momentum: {d['momentum']}\n\n"
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

def main_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Forex Currencies", callback_data="menu_currencies")],
        [InlineKeyboardButton("🔔 Price Alert", callback_data="menu_alerts"),
         InlineKeyboardButton("📰 Market News", callback_data="market_news")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings")],
    ])

def settings_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌍 Language", callback_data="set_lang")],
        [InlineKeyboardButton("📊 Default Pairs", callback_data="set_pairs")],
        [InlineKeyboardButton("🔕 Alert Sound", callback_data="set_sound")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")],
    ])

def category_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔵 Major Pairs", callback_data="cat_major")],
        [InlineKeyboardButton("💛 Gold & Oil", callback_data="cat_gold")],
        [InlineKeyboardButton("📈 Minor Pairs", callback_data="cat_minor")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")],
    ])

def pairs_kb(pairs, back):
    keys = list(pairs.keys())
    rows = [[InlineKeyboardButton(k, callback_data=f"analyze_{k}") for k in keys[i:i+2]]
            for i in range(0, len(keys), 2)]
    rows.append([InlineKeyboardButton("🔙 Back", callback_data=back),
                 InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")])
    return InlineKeyboardMarkup(rows)

def after_analysis_kb(symbol, back):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Refresh", callback_data=f"analyze_{symbol}"),
         InlineKeyboardButton("🔙 Back", callback_data=back)],
        [InlineKeyboardButton("🔔 Set Alert", callback_data=f"alert_{symbol}")],
    ])

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 FOREX ANALYSIS BOT\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Welcome to AI Forex Analysis! 👋\n"
        "Select an option below 👇",
        reply_markup=main_menu_kb()
    )

async def button(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    
    if data == "main_menu":
        await q.edit_message_text(
            "🤖 FOREX ANALYSIS BOT\n━━━━━━━━━━━━━━━━━━━━\n\nWelcome! Select an option 👇",
            reply_markup=main_menu_kb()
        )
    elif data == "menu_settings":
        await q.edit_message_text(
            "⚙️ Settings\n━━━━━━━━━━━━━━━━━━━━\n\nChoose an option:",
            reply_markup=settings_kb()
        )
    elif data == "menu_alerts":
        alerts = load_alerts()
        text = "🔔 Price Alert\n━━━━━━━━━━━━━━━━━━━━\n\n"
        user_id = update.effective_user.id
        user_alerts = {k: v for k, v in alerts.items() if str(k).endswith(str(user_id))}
        if user_alerts:
            for item, price in user_alerts.items():
                pair = item.split("_")[0]
                text += f"• {pair}: {price}\n"
        else:
            text += "No active alerts.\n"
        text += "\n\nTo set a new alert:\n/setalert [SYMBOL] [PRICE]\nExample: /setalert EUR/USD 1.2000"
        await q.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
            ])
        )
    elif data == "market_news":
        await q.edit_message_text("⏳ Fetching latest news...")
        news = get_news()
        await q.edit_message_text(
            news,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Refresh", callback_data="market_news"),
                 InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
            ])
        )
    elif data in ["set_lang", "set_pairs", "set_sound"]:
        await q.edit_message_text(
            "🚧 Coming Soon!\nThis feature will be available soon.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="menu_settings")]
            ])
        )
    elif data.startswith("alert_"):
        symbol = data.replace("alert_", "")
        await q.edit_message_text(
            f"🔔 Set Alert for {symbol}\n━━━━━━━━━━━━━━━━━━━━\n\nSend:\n/setalert {symbol} [price]\n\nExample: /setalert {symbol} 1.2000",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="analyze_"+symbol)]
            ])
        )
    elif data == "menu_currencies":
        await q.edit_message_text(
            "💱 SELECT CATEGORY\n━━━━━━━━━━━━━━━━━━━━\n\nChoose a category 👇",
            reply_markup=category_kb()
        )
    elif data == "cat_major":
        await q.edit_message_text(
            "🔵 MAJOR PAIRS\n━━━━━━━━━━━━━━━━━━━━\n\nSelect a pair 👇",
            reply_markup=pairs_kb(MAJOR_PAIRS, "menu_currencies")
        )
    elif data == "cat_gold":
        await q.edit_message_text(
            "💛 GOLD & OIL\n━━━━━━━━━━━━━━━━━━━━\n\nSelect a pair 👇",
            reply_markup=pairs_kb(GOLD_OIL, "menu_currencies")
        )
    elif data == "cat_minor":
        await q.edit_message_text(
            "📈 MINOR PAIRS\n━━━━━━━━━━━━━━━━━━━━\n\nSelect a pair 👇",
            reply_markup=pairs_kb(MINOR_PAIRS, "menu_currencies")
        )
    elif data.startswith("analyze_"):
        symbol = data.replace("analyze_", "")
        await q.edit_message_text(f"⏳ Analyzing {symbol}...")
        result = get_analysis(symbol)
        if result:
            back = "cat_major" if symbol in MAJOR_PAIRS else \
                   "cat_gold" if symbol in GOLD_OIL else "cat_minor"
            await q.edit_message_text(
                format_analysis(result),
                reply_markup=after_analysis_kb(symbol, back)
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
        alerts = load_alerts()
        key = f"{symbol}_{update.effective_user.id}"
        alerts[key] = price
        save_alerts(alerts)
        await update.message.reply_text(f"✅ Alert set for {symbol} at {price}\nWe'll notify you when price reaches this level!")
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
