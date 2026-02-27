import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# 1. إعداد خادم Flask بسيط لإيهام Render أن التطبيق هو موقع ويب
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    # Render يمرر المنفذ تلقائياً عبر متغير البيئة PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. إعدادات البوت (Intents)
intents = discord.Intents.default()
intents.members = True          # ضروري للترحيب بالأعضاء
intents.message_content = True  # ضروري لقراءة محتوى الرسائل

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ تم تسجيل الدخول باسم: {bot.user.name}')

@bot.event
async def on_member_join(member):
    # تأكد أن اسم القناة مطابق تماماً لما هو موجود في سيرفرك
    channel = discord.utils.get(member.guild.channels, name='✈️welcome')
    if channel:
        embed = discord.Embed(
            description=f"**حيّاك الله** {member.mention} في سيرفرنا! 🎉",
            color=0x2f3136
        )
        embed.set_image(url=member.display_avatar.url)
        await channel.send(embed=embed)

# 3. تشغيل الخادم ثم البوت
if __name__ == "__main__":
    keep_alive()  # تشغيل Flask في الخلفية
    
    token = os.getenv('DISCORD_TOKEN')
    if token:
        bot.run(token)
    else:
        print("❌ خطأ: لم يتم العثور على DISCORD_TOKEN في متغيرات البيئة!")
