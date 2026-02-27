import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# --- إعداد Flask لإبقاء الخدمة تعمل ---
app = Flask('')

@app.route('/')
def home():
    return "I'm alive!"

def run():
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- كود البوت الخاص بك ---
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as: {bot.user.name}')

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.channels, name='✈️welcome')
    if channel:
        embed = discord.Embed(
            description=f"**حيّاك الله** {member.mention}",
            color=0x2f3136
        )
        embed.set_image(url=member.display_avatar.url)
        await channel.send(embed=embed)

# تشغيل Flask ثم البوت
keep_alive()
token = os.getenv('DISCORD_TOKEN')
bot.run(token)

