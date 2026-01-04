import os
import discord
from discord.ext import tasks, commands
from datetime import datetime, timedelta
import pytz

# ===== 設定區 =====
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = 1457376914867097691
TIMEZONE = pytz.timezone("Asia/Taipei")
REMIND_HOUR = 22
REMIND_MINUTE = 15
# ==================

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot 已上線：{bot.user}")
    daily_reminder.start()

@tasks.loop(minutes=1)
async def daily_reminder():
    now = datetime.now(TIMEZONE)

    if now.hour == REMIND_HOUR and now.minute == REMIND_MINUTE:
        try:
            # 取得頻道對象
            channel = await bot.fetch_channel(CHANNEL_ID)
            permissions = channel.permissions_for(channel.guild.me)

            if not permissions.send_messages:
                print(f"Bot 沒有發訊息權限到頻道 {channel.name} ({channel.id})")
                return

            # 決定是否可以用 @everyone
            prefix = "@everyone\n\n" if permissions.mention_everyone else ""

            content = (
                f"{prefix}📢 **活動公告**\n\n"
                f"🕙 現在時間：{now.strftime('%H:%M')}\n"
                "📌 提醒事項：記得百業活動\n\n"
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

        # 避免同一分鐘內重複發送
        next_minute = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
        await discord.utils.sleep_until(next_minute)

bot.run(TOKEN)
