from flask import Flask
import threading
import discord
from discord.ext import tasks, commands
from datetime import datetime, timedelta
import pytz
import asyncio
import os

# ===== Discord Bot 設定 =====
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = 1457376914867097691
TIMEZONE = pytz.timezone("Asia/Taipei")

TIME_REMINDERS = {
    (22, 20): "📌 提醒事項：記得百業活動"
}

WEEKDAY_REMINDERS = {

    (3, 21, 0): "📌 提醒事項：一決高下",
    (5, 21, 0): "📌 提醒事項：一決高下",
    (2, 21, 30): "📌 提醒事項：破軍殺將",
    (5, 21, 30): "📌 提醒事項：破軍殺將",
    (0, 21, 30): "📌 提醒事項：晚上10:30百業派對完百業俠境" 
}

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot 已上線：{bot.user}")
    daily_reminder.start()

@tasks.loop(minutes=1)
async def daily_reminder():
    now = datetime.now(TIMEZONE)
    current_time = (now.hour, now.minute)
    weekday_time = (now.weekday(), now.hour, now.minute)
    message_text = None

    if current_time in TIME_REMINDERS:
        message_text = TIME_REMINDERS[current_time]
    elif weekday_time in WEEKDAY_REMINDERS:
        message_text = WEEKDAY_REMINDERS[weekday_time]

    if message_text:
        try:
            channel = await bot.fetch_channel(CHANNEL_ID)
            permissions = channel.permissions_for(channel.guild.me)
            if not permissions.send_messages:
                print(f"Bot 沒有發訊息權限到頻道 {channel.name}")
                return

            prefix = "@everyone\n\n" if permissions.mention_everyone else ""
            content = (
                f"{prefix}📢 **活動公告**\n\n"
                f"🕙 現在時間：{now.strftime('%a %H:%M')}\n"
                f"{message_text}\n\n— 系統自動公告 —"
            )
            await channel.send(content)
            print(f"訊息已發送到 {channel.name}")

        except Exception as e:
            print(f"發訊息錯誤: {e}")

# ===== Flask Web 服務 =====
app = Flask(__name__)

@app.route("/")
def home():
    return "Discord Bot on going！"

def run_flask():
    app.run(host="0.0.0.0", port=10000)  # Render 可偵測的端口

# ===== 啟動 Web 服務與 Bot =====
threading.Thread(target=run_flask).start()
bot.run(TOKEN)
