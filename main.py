import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# --- إعداد Flask لإبقاء البوت مستيقظاً على Render ---
app = Flask('')

@app.route('/')
def home():
    return "Welcome Bot is Online!"

   def run():
    # Render يرسل رقم المنفذ في متغير بيئة اسمه PORT
    port = int(os.environ.get("PORT", 8080))
    # استخدام 0.0.0.0 ضروري جداً ليعمل على السيرفر
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# --- إعدادات البوت ---
intents = discord.Intents.default()
intents.members = True  # ضروري جداً لرصد دخول الأعضاء الجدد

bot = commands.Bot(command_prefix='!', intents=intents)

# --- نظام الترحيب ---

@bot.event
async def on_ready():
    print(f'✅ بوت الترحيب يعمل الآن باسم: {bot.user.name}')

@bot.event
async def on_member_join(member):
    # ضع هنا ID القناة التي تريد الترحيب فيها
    WELCOME_CHANNEL_ID = 1476529909558935655  
    
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    
    if channel:
        try:
            # إعداد رسالة الترحيب (Embed)
            embed = discord.Embed(
                title="عضو جديد انضم إلينا! ✨",
                description=f"حيّاك الله {member.mention} في سيرفرنا، نورتنا بقدومك! 🎉",
                color=0x2f3136 # يمكنك تغيير اللون حسب رغبتك
            )
            
            # إضافة صورة العضو وصورة السيرفر
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f"أنت العضو رقم {len(list(member.guild.members))}")
            
            await channel.send(content=member.mention, embed=embed)
            print(f"✅ تم إرسال الترحيب لـ {member.name}")
            
        except Exception as e:
            print(f"❌ خطأ أثناء إرسال رسالة الترحيب: {e}")
    else:
        print("❌ لم يتم العثور على قناة الترحيب، تأكد من الـ ID ومن وجود البوت في القناة.")

# --- تشغيل البوت ---
if __name__ == "__main__":
    keep_alive() # تشغيل السيرفر الوهمي
    
    # تأكد من إضافة DISCORD_TOKEN في إعدادات Render (Environment Variables)
    token = os.getenv('DISCORD_TOKEN')
    if token:
        bot.run(token)
    else:
        print("❌ خطأ: لم يتم العثور على التوكن في إعدادات Render!")
