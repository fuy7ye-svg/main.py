import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# --- إعداد Flask لإبقاء البوت مستيقظاً ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is Online!"

def run():
    # تأكد أن هذا السطر والسطر الذي يليه يبدآن بـ 4 مسافات
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- إعدادات البوت ---
intents = discord.Intents.default()
intents.members = True          
intents.message_content = True  

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ تم تشغيل البوت بنجاح: {bot.user.name}')

@bot.event
async def on_member_join(member):
    # ID القناة الخاص بك
    WELCOME_CHANNEL_ID = 1476529909558935655  
    
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    
    if channel:
        try:
            embed = discord.Embed(
                description=f"**حيّاك الله** {member.mention} في سيرفرنا! 🎉",
                color=0x2f3136
            )
            # جلب صورة العضو
            avatar_url = member.display_avatar.url
            embed.set_image(url=avatar_url)
            
            await channel.send(embed=embed)
            print(f"✅ تم إرسال الترحيب لـ {member.name}")
        except Exception as e:
            print(f"❌ خطأ أثناء إرسال الرسالة: {e}")
    else:
        print("❌ لم يتم العثور على القناة، تأكد من الـ ID.")

# --- تشغيل البوت ---
if __name__ == "__main__":
    keep_alive()  # تشغيل خادم الويب
    
    token = os.getenv('DISCORD_TOKEN')
    if token:
        bot.run(token)
    else:
        print("❌ خطأ: لم يتم العثور على DISCORD_TOKEN!")
