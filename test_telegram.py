from telegram_alert import send_alert


message = (
    "🚀 ICT LIQUIDITY ALERT BOT\n\n"
    "✅ Telegram connection successful!\n\n"
    "Market Data: ✅\n"
    "Liquidity: ✅\n"
    "CRT: ✅\n"
    "FVG: ✅\n"
    "Order Block: ✅"
)


try:
    send_alert(message)
    print("✅ Telegram test message sent successfully!")

except Exception as e:
    print("❌ Telegram test failed")
    print(str(e))
