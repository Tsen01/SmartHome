import logging
import os
import dotenv
import nextcord
from nextcord.ext import commands
import firebase_admin
from firebase_admin import credentials
from databaseURL import databaseURL     # Firebase Realtime Database URL

logging.basicConfig(level=logging.INFO, format='[DISCORD_BOT_INFO] %(message)s')

dotenv.load_dotenv()

if os.getenv("DEPLOYMENT_ENV") == "prod":
    dotenv.load_dotenv("../config/.env.prod")

elif os.getenv("DEPLOYMENT_ENV") == "beta":
    dotenv.load_dotenv("../config/.env.beta")

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

GUILD_IDS = [int(value) for value in os.getenv("GUILD_IDS").split(",")]
ADMIN_IDS = [int(value) for value in os.getenv("ADMIN_IDS").split(",")]

# Enable intents
intents = nextcord.Intents.all()
intents.message_content = True

bot = commands.Bot(intents=intents)

# Firebase setup (initialize only once)
cred = credentials.Certificate("../Router/json/firebase.json")
firebase_app = firebase_admin.initialize_app(cred, {
    "databaseURL": databaseURL
})

# Load extensions(cogs)
for filename in os.listdir('cogs'):
    if filename.endswith('.py') and filename != '__init__.py':
        bot.load_extension(f'cogs.{filename[:-3]}')

# Event triggered when the bot is ready
@bot.event
async def on_ready():
    activity = nextcord.ActivityType.streaming   # Set the activity type to "streaming"
    logging.info(f'We have logged in as {bot.user}')  # 紀錄 DC bot login information
    # 設定機器人狀態
    await bot.change_presence(status=nextcord.Status.dnd, activity=nextcord.Activity(type=activity, name="SmartHome"))

# Define a slash command to reload extensions
@bot.slash_command()
async def reload(ctx, extension: str):
    if ctx.user.id in ADMIN_IDS:
        bot.reload_extension(f'cogs.{extension}')
        await ctx.send(f'Reloaded: {extension}', ephemeral=True)
    else:
        await ctx.send('You are not an administrator.', ephemeral=True)

# Define a command to get user information
@bot.command()
async def userinfo(ctx):
    member = ctx.author  # 知道發出指令的使用者
    roles = [role.name for role in member.roles[1:]]

    # Send user information
    await ctx.send(
        f"User name: {member.name}\n"
        f"User ID: {member.id}\n"
        f"Joined at: {member.joined_at}\n"
        f"Roles: {', '.join(roles)}"
    )

# Event to handle messages
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.lower() == "hello":
        await message.channel.send(f"Hello, {message.author.name}!")

    await bot.process_commands(message)


if __name__ == '__main__':
    bot.run(DISCORD_BOT_TOKEN)