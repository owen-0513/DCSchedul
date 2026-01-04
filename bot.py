import os
import discord
from discord.ext import tasks, commands
from datetime import datetime, timedelta
import pytz
import asyncio 

TOKEN = os.getenv("DISCORD_TOKEN")  
CHANNEL_ID = 1457376914867097691  
TIMEZONE = pytz.timezone("Asia/Taipei") 

# 單純時間提醒 (每天)
TIME_REMINDERS = {
    (21, 20): "📌 提醒事項：記得百業活動"
}

# 星期 + 時間提醒
WEEKDAY_REMINDERS = {
    (3, 21, 0): "📌 提醒事項：一決高下",       # 星期四 晚上9點
    (5, 21, 0): "📌 提醒事項：一決高下",       # 星期六 晚上9點
    (2, 21, 30): "📌 提醒事項：破軍殺將",     # 星期三 晚上9點半
    (5, 21, 30): "📌 提醒事項：破軍殺將"      # 星期六 晚上9點半
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
    weekday_time = (now.weekday(), now.hour, now.minute)  # 星期 + 時間

    message_text = None

    # 先檢查每天時間提醒
    if current_time in TIME_REMINDERS:
        message_text = TIME_REMINDERS[current_time]

    # 再檢查星期時間提醒
    elif weekday_time in WEEKDAY_REMINDERS:
        message_text = WEEKDAY_REMINDERS[weekday_time]

    # 如果有訊息要發送
    if message_text:
        try:
            channel = await bot.fetch_channel(CHANNEL_ID)
            permissions = channel.permissions_for(channel.guild.me)

            if not permissions.send_messages:
                print(f"Bot 沒有發訊息權限到頻道 {channel.name} ({channel.id})")
                return

            prefix = "@everyone\n\n" if permissions.mention_everyone else ""

            content = (
                f"{prefix}📢 **活動公告**\n\n"
                f"🕙 現在時間：{now.strftime('%a %H:%M')}\n"
                f"{message_text}\n\n"
                "— 系統自動公告 —"
            )

            await channel.send(content)
            print(f"訊息已發送到 {channel.name} ({channel.id})")

        except discord.Forbidden:
            print("Bot 無法存取此頻道或權限不足")
        except discord.HTTPException as e:
            print(f"發訊息失敗: {e}")
        except Exception as e:
            print(f"其他錯誤: {e}")

        next_minute = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
        await asyncio.sleep((next_minute - now).total_seconds()) 

bot.run(TOKEN)
