import discord
from discord import app_commands
from discord.ext import commands
import datetime

# Bot setup with all intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
        bot.start_time = datetime.datetime.utcnow()
        
        # Generate and display bot invite link
        invite_link = discord.utils.oauth_url(
            bot.user.id,
            permissions=discord.Permissions(administrator=True),
            scopes=["bot", "applications.commands"]
        )
        print(f"\nInvite the bot to your server using this link:\n{invite_link}")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.event
async def on_guild_join(guild):
    # Send welcome message to the first available text channel
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            embed = discord.Embed(
                title="Thanks for adding me!",
                description="Use `/help` to see my commands.",
                color=discord.Color.green()
            )
            await channel.send(embed=embed)
            break

@bot.tree.command(name="stats", description="Show bot statistics")
async def stats(interaction: discord.Interaction):
    uptime = datetime.datetime.utcnow() - bot.start_time
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    embed = discord.Embed(title="Bot Statistics", color=discord.Color.blue())
    embed.add_field(name="Bot Name", value=bot.user.name, inline=True)
    embed.add_field(name="Bot ID", value=bot.user.id, inline=True)
    embed.add_field(name="Servers", value=len(bot.guilds), inline=True)
    embed.add_field(name="Users", value=len(set(bot.users)), inline=True)
    embed.add_field(name="Ping", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="Uptime", value=f"{days}d {hours}h {minutes}m {seconds}s", inline=True)

    if bot.user.avatar:
        embed.set_thumbnail(url=bot.user.avatar.url)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ping", description="Check bot's latency")
async def ping(interaction: discord.Interaction):
    embed = discord.Embed(title="🏓 Pong!", color=discord.Color.green())
    embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="help", description="Show all available commands")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(title="Bot Commands", description="Here are all available commands:", color=discord.Color.blue())
    embed.add_field(name="/help", value="Show this help message", inline=False)
    embed.add_field(name="/stats", value="Show bot statistics", inline=False)
    embed.add_field(name="/ping", value="Check bot's latency", inline=False)
    embed.add_field(name="/uptime", value="Check bot's uptime", inline=False)
    embed.add_field(name="/invite", value="Get bot's invite link", inline=False)
    embed.add_field(name="/avatar", value="View User's avatar", inline=False)
    embed.add_field(name="/afk", value="Set your AFK status", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="invite", description="Get bot's invite link")
async def invite(interaction: discord.Interaction):
    invite_link = discord.utils.oauth_url(
        bot.user.id,
        permissions=discord.Permissions(administrator=True),
        scopes=["bot", "applications.commands"]
    )
    embed = discord.Embed(title="Invite Bot", description=f"[Click here to invite the bot]({invite_link})", color=discord.Color.green())
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="uptime", description="Check bot's Uptime")
async def uptime(interaction: discord.Interaction):
    uptime = datetime.datetime.utcnow() - bot.start_time
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    embed = discord.Embed(title="Bot's Uptime", color=discord.Color.green())
    embed.add_field(name="Uptime", value=f"{days} days, {hours} hours,{minutes} minutes {seconds} secconds", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="avatar", description="View a user's avatar")
async def avatar(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    embed = discord.Embed(title=f"{user.name}'s Avatar", color=discord.Color.blue())
    embed.set_image(url=user.avatar.url if user.avatar else user.default_avatar.url)
    await interaction.response.send_message(embed=embed)

# Store AFK users and their messages
afk_users = {}

@bot.tree.command(name="afk", description="Set your AFK status with an optional message")
async def afk(interaction: discord.Interaction, message: str = "AFK"):
    user_id = interaction.user.id
    afk_users[user_id] = message
    embed = discord.Embed(description=f"I set your AFK: {message}", color=discord.Color.yellow())
    await interaction.response.send_message(embed=embed)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Check if mentioned user is AFK
    for mention in message.mentions:
        if mention.id in afk_users:
            afk_message = afk_users[mention.id]
            embed = discord.Embed(description=f"{mention.name} is AFK: {afk_message}", color=discord.Color.yellow())
            await message.reply(embed=embed)

    # Remove AFK status if user types a message
    if message.author.id in afk_users:
        del afk_users[message.author.id]
        embed = discord.Embed(description=f"Welcome back {message.author.name}, I removed your AFK status!", color=discord.Color.green())
        await message.channel.send(embed=embed)

    await bot.process_commands(message)

# Replace 'YOUR_TOKEN' with your bot token from Discord Developer Portal
bot.run('Youtoken')
