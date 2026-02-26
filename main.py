import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# --- إعداد Flask لتجاوز خطأ Port Scan في Render ---
app = Flask('')

@app.route('/')
def home():
    return "البوت يعمل بنجاح!"

def run_flask():
    # Render يتطلب ربط الخدمة بـ Port معين تلقائياً
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# --- إعدادات البوت ---
intents = discord.Intents.default()
intents.message_content = True  # يجب تفعيلها من Discord Developer Portal
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- نظام التذاكر (الأزرار) ---

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="إغلاق التذكرة 🔒", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("سيتم حذف القناة خلال ثوانٍ...")
        await interaction.channel.delete()

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="فتح تذكرة 📩", style=discord.ButtonStyle.primary, custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        
        # اسم القناة
        channel_name = f"ticket-{user.name.lower()}"
        
        # التحقق من وجود تذكرة مفتوحة
        existing_channel = discord.utils.get(guild.text_channels, name=channel_name)
        if existing_channel:
            return await interaction.response.send_message(f"لديك تذكرة مفتوحة بالفعل: {existing_channel.mention}", ephemeral=True)

        # الصلاحيات (المستخدم والإدارة فقط)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites)
        
        embed = discord.Embed(
            title="تذكرة جديدة",
            description=f"مرحباً {user.mention}، سيتم الرد عليك قريباً من قبل الإدارة.",
            color=discord.Color.blue()
        )
        await channel.send(embed=embed, view=CloseTicketView())
        await interaction.response.send_message(f"تم فتح تذكرتك: {channel.mention}", ephemeral=True)

# --- الأحداث ---

@bot.event
async def on_ready():
    print(f'✅ سجلت الدخول باسم: {bot.user}')
    # تسجيل الأزرار لتعمل دائماً
    bot.add_view(TicketView())
    bot.add_view(CloseTicketView())

@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    embed = discord.Embed(
        title="نظام التذاكر",
        description="اضغط على الزر أدناه لفتح تذكرة جديدة والتواصل مع الدعم.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed, view=TicketView())

# --- التشغيل ---
if __name__ == "__main__":
    keep_alive() # تشغيل السيرفر الوهمي لـ Render
    token = os.getenv('DISCORD_TOKEN') # تأكد من إضافة التوكن في إعدادات Render
    if token:
        bot.run(token)
    else:
        print("❌ لم يتم العثور على التوكن! تأكد من إضافته في Environment Variables باسم DISCORD_TOKEN")
