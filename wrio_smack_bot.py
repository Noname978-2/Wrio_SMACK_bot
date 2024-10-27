import discord
from discord.ext import commands
import random
import json
import os
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv



intents = discord.Intents.all()
intents.messages = True  
intents.guilds = True 
intents.voice_states = True  

bot = commands.Bot(command_prefix='!', intents=intents)

DATA_FILE  = 'smack_stat.json'

def load_stats():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_stats():
    with open(DATA_FILE, 'w') as f:
        json.dump(smack_stat, f)

smack_stat = load_stats()

@bot.command()
async def wrio_smack(ctx):
    user = str(ctx.author)
    now = datetime.now()
    
    if user in smack_stat and 'last_hit' in smack_stat[user]:
        last_hit_time = datetime.fromisoformat(smack_stat[user]['last_hit'])
        if now < last_hit_time + timedelta(hours = 4):
            remaining_time = (last_hit_time + timedelta(hours=4)) - now
            await ctx.send(f'{ctx.author.mention}, ви можете вдарити бота знову через {remaining_time.total_seconds() // 3600:.0f} годин(и) та {remaining_time.total_seconds() % 3600 // 60:.0f} хвилин(и).')
            return

    amount = random.randint(1, 10) 
    if user not in smack_stat:
        smack_stat[user] = {'count': 0, 'last_hit': now.isoformat()}
    else:
        smack_stat[user]['count'] += amount
        smack_stat[user]['last_hit'] = now.isoformat()

    save_stats()

    embed = discord.Embed(
        title="Успіх!",
        description=f'{ctx.author.mention}, ви вдарили Райотслі по дупі {amount} разів!',
        color=discord.Color.green()
    )
    
    await ctx.send(embed=embed)


@bot.command()
async def wrio_stats(ctx):
    user = str(ctx.author)
    if user not in smack_stat:
        embed = discord.Embed(
            title="Статистика",
            description=f'{ctx.author.mention}, ви ще не били Райостлі по дупі.',
            color=discord.Color.red()
        )
    else:
        embed = discord.Embed(
            title="Статистика",
            description=f"{ctx.author.mention}, ви вдарили Райостлі по дупі {smack_stat[user]['count']} разів.",
            color=discord.Color.blue() 
        )
    
    await ctx.send(embed=embed)

@bot.command()
async def wrio_global(ctx):
    if not smack_stat:
        embed = discord.Embed(
            title = "Тут поки що пусто...",
            description=f'...',
            color=discord.Color.black()
        )
    else:
        global_stat = ''
        for user, v in smack_stat.items():
            amount = v['count']
            global_stat += f'{user}: {amount} ударів\n'
        embed = discord.Embed(
            title = "Загальна статистика",
            description=global_stat,
            color=discord.Color.purple()
        )

    await ctx.send(embed=embed)       

@bot.command()
async def wrio_neuvi(ctx):
    if ctx.author.voice is None:
        await ctx.send(f"{ctx.author.mention}, ви повинні бути в голосовому каналі!")
        return

    channel = ctx.author.voice.channel
    voice_client = await channel.connect()
    source = discord.FFmpegPCMAudio('neuvi.mp3')
    voice_client.play(source)

    await asyncio.sleep(31)

    await voice_client.disconnect()


@bot.command()
async def wrio_help(ctx):
    help_text = """
  `!wrio_smack` - Вдарити Райотслі по дупі
  `!wrio_stats` - Переглянути статистику
  `!wrio_help` - Список команд
    """
    embed = discord.Embed(
        title="Доступні команди:",
        description=help_text,
        color=discord.Color.gold()  
    )
    
    await ctx.send(embed=embed)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(TOKEN)
