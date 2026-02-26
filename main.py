import discord
from discord.ext import commands
from discord import app_commands
import os
from flask import Flask
from threading import Thread

# --- إعداد Flask لإبقاء البوت حياً (Keep Alive) ---
app = Flask('')

@app.route('/')
def home():
    return "I am alive!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# --- إعدادات البوت الأساسية ---
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True # تأكد من تفعيلها في بوابة المطورين

bot = commands.Bot(command_prefix="!", intents=intents)

# --- نظام التذاكر (الواجهة والأزرار) ---

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="إغلاق التذكرة 🔒", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("سيتم إغلاق هذه التذكرة وحذف القناة خلال ثوانٍ...")
        await interaction.channel.delete()

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="فتح تذكرة 📩", style=discord.ButtonStyle.success, custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        
        # تسمية القناة باسم المستخدم
        channel_name = f"ticket-{user.name}".lower().replace(" ", "-")
        
        # التحقق إذا كانت القناة موجودة
        existing_channel = discord.utils.get(guild.text_channels, name=channel_name)
        if existing_channel:
            return await interaction.response.send_message(f"لديك تذكرة مفتوحة بالفعل هنا: {existing_channel.mention}", ephemeral=True)

        # إعداد الصلاحيات (المستخدم + الإدارة فقط)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        # إنشاء القناة
        ticket_channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites)
        
        embed = discord.Embed(
            title="نظام الدعم الفني",
            description=f"مرحباً {user.mention}، فضلاً اكتب مشكلتك هنا وسيرد عليك الإداريون قريباً.",
            color=discord.Color.green()
        )
        
        await ticket_channel.send(embed=embed, view=CloseTicketView())
        await interaction.response.send_message(f"تم إنشاء تذكرتك بنجاح: {ticket_channel.mention}", ephemeral=True)

# --- أحداث البوت ---

@bot.event
async def on_ready():
    print(f'✅ تم تسجيل الدخول باسم: {bot.user}')
    # تفعيل الأزرار بشكل دائم حتى لو ريسترت البوت
    bot.add_view(TicketView())
    bot.add_view(CloseTicketView())
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

# --- أوامر التحكم ---

@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    embed = discord.Embed(
        title="تذاكر المساعدة 🎟️",
        description="إذا كنت تواجه مشكلة أو تريد التواصل مع الإدارة، اضغط على الزر أدناه.",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed, view=TicketView())

# --- تشغيل البوت ---
if __name__ == "__main__":
    keep_alive() # تشغيل Flask في الخلفية
    token = os.getenv('DISCORD_TOKEN')
    if token:
        bot.run(token)
    else:
        print("❌ خطأ: لم يتم العثور على DISCORD_TOKEN في متغيرات البيئة!")
