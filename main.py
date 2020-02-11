#from yandex_music.client import Client
##from yandex_music.search import Search, SearchResult

##client = Client()
##client = Client.from_credentials('serheo99@yandex.ru', 'Sn32089461')
##client.users_likes_tracks()[0].track.download('example.mp3')


import discord
from discord.ext import commands

TOKEN = 'Njc2NzIyNjczMjAzNTQ0MDc1.XkJ2hQ.wXUKr4LgekgnEwHtmwyhR-2N70w'
bot = commands.Bot(command_prefix='!')


@bot.command(pass_context=False)  # разрешаем передавать агрументы
async def test(ctx, arg):  # создаем асинхронную фунцию бота
	await ctx.send("Hello, World!")  # отправляем обратно аргумент

bot.run(TOKEN)
