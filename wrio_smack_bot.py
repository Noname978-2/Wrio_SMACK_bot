import discord
from discord.ext import commands
import random
import json
import os
import asyncio
import traceback
from datetime import datetime, timedelta
from dotenv import load_dotenv
from discord import FFmpegPCMAudio, FFmpegOpusAudio
from discord.utils import get
import subprocess
from collections import deque
import yt_dlp


queues = {}

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
        if now < last_hit_time + timedelta(seconds = 4):
            remaining_time = (last_hit_time + timedelta(seconds=4)) - now
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
        description=f'{ctx.author.mention}, ви щойно вдарили Райотслі по дупі {amount} разів!',
        color=discord.Color.green()
    )
    
    await ctx.send(embed=embed)

@bot.command()
async def wrio_ping(ctx):
    latency = bot.latency 
    embed = discord.Embed(
        title="smack",
        description=f"Затримка: `{latency * 1000:.2f} мс`",
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
    """НЕ ПРАЦЮЄ"""
    if not ctx.author.voice:
        return await ctx.send("🔊 Помилка: ви не в голосовому каналі!")

    try:
        voice = ctx.voice_client
        
        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -nostdin -thread_queue_size 1024',
            'options': '-vn -filter:a "volume=0.8" -ac 2 -ar 48000 -b:a 128k -max_alloc 50000000',
            'executable': 'ffmpeg.exe'
        }

        audio_path = os.path.abspath('euvi_OGG.ogg')  
        if voice is None:
            voice = await ctx.author.voice.channel.connect(timeout=30.0, reconnect=True)
        elif voice.channel != ctx.author.voice.channel:
            await voice.move_to(ctx.author.voice.channel)

        if voice.is_playing():
            voice.stop()

        source = discord.FFmpegOpusAudio(
            source=audio_path,
            **ffmpeg_options
        )

        def after_play(error):
            if error:
                print(f"FFmpeg Error: {error}")
                asyncio.run_coroutine_threadsafe(
                    ctx.send(f"Playback error: {error}"), 
                    bot.loop
                )

        voice.play(source, after=after_play)
        await ctx.send("🎵 Процес...")

    except Exception as e:
        await ctx.send(f"Critical error (ура, критшанс прокнув): {str(e)}")
        print(f"Full error: {traceback.format_exc()}")


@bot.command()
async def wrio_help(ctx):
    help_text = """
  `!wrio_smack` - Вдарити Райотслі по дупі  
  `!wrio_stats` - Переглянути свою статистику ударів  
  `!wrio_global` - Переглянути загальну статистику всіх гравців  
  `!wrio_ping` - Перевірити затримку бота   
  `!wrio_play <url>` - Додати аудіо з ютубу до черги  
  `!queue` - Показати поточну чергу відтворення  
  `!skip` - Пропустити трек  
  `!leave` - Від'єднати бота з голосового каналу  
  `!wrio_neuvi` - (Не працює, тому що лол)  
  `!wrio_help - хз
    """
    embed = discord.Embed(
        title="📜 Список команд:",
        description=help_text,
        color=discord.Color.gold()
    )
    await ctx.send(embed=embed)


@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Бот відключився від голосового каналу")
    else:
        await ctx.send("Бот не підключений до голосового каналу")

@wrio_neuvi.before_invoke
async def ensure_voice_permissions(ctx):
    if not ctx.author.guild_permissions.connect:
        raise commands.CommandError("У вас немає прав для підключення до голосових каналів")



@bot.command()
async def wrio_play(ctx, url: str):
    """Додає аудіо до черги з YouTube/SoundCloud"""
    if not ctx.author.voice:
        return await ctx.send("☦️ Помилка: ви не в голосовому каналі!")
    
    try:
        if ctx.guild.id not in queues:
            queues[ctx.guild.id] = deque()
            
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'entries' in info:  
                info = info['entries'][0]
                
            track = {
                'url': info['url'],
                'title': info.get('title', 'Невідомий трек'),
                'requester': ctx.author
            }
            
        queues[ctx.guild.id].append(track)
        await ctx.send(f"🎵 Додано до черги: {track['title']}")
        
        voice = ctx.voice_client
        if not voice or not voice.is_playing():
            await play_next(ctx)
            
    except Exception as e:
        await ctx.send(f"❌ Помилка: {str(e)}")

async def play_next(ctx):
    """Відтворює наступний трек з черги"""
    if ctx.guild.id not in queues or not queues[ctx.guild.id]:
        return
        
    voice = ctx.voice_client
    
    if not voice:
        voice = await queues[ctx.guild.id][0]['requester'].voice.channel.connect()
    elif voice.is_playing():
        voice.stop()
        
    track = queues[ctx.guild.id].popleft()

    ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 10 -nostdin',
    'options': (
        '-vn '
        '-af "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=async=1:min_hard_comp=0.100:first_pts=0" '
        '-ac 2 '
        '-ar 48000 '
        '-b:a 320k '
        '-bufsize 4096k '
        '-threads 2'
    ),
    'executable': 'ffmpeg'
    }


    
    
    def after_playing(error):
        if error:
            print(f"Помилка відтворення: {error}")
        asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)
    
    source = FFmpegPCMAudio(track['url'], **ffmpeg_options)
    voice.play(source, after=after_playing)
    await ctx.send(f"🎵 Зараз грає: {track['title']} | Запитав: {track['requester'].mention}")

@bot.command()
async def queue(ctx):
    """Показує поточну чергу відтворення"""
    if ctx.guild.id not in queues or not queues[ctx.guild.id]:
        return await ctx.send("Черга порожня!")
    
    embed = discord.Embed(title="Черга відтворення", color=0x00ff00)
    for i, track in enumerate(queues[ctx.guild.id], 1):
        embed.add_field(
            name=f"{i}. {track['title']}",
            value=f"Запитав: {track['requester'].display_name}",
            inline=False
        )
    await ctx.send(embed=embed)

@bot.command()
async def skip(ctx):
    """Пропускає поточний трек"""
    voice = ctx.voice_client
    if voice and voice.is_playing():
        voice.stop()
        await ctx.send("⏩ Трек пропущено")
        await play_next(ctx)
    else:
        await ctx.send("Нічого не грає!")


from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Бот живий!"

def run():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run).start()


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(TOKEN)

