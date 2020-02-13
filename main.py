#from yandex_music.client import Client
##from yandex_music.search import Search, SearchResult

##client = Client()
##client = Client.from_credentials('serheo99@yandex.ru', 'Sn32089461')
##client.users_likes_tracks()[0].track.download('example.mp3')


import discord
from discord.ext import commands

TOKEN = 'Njc2NDU5NDQ1Nzc3MDcyMTMx.XkPngQ.tvpRDqztbDBESGgIxXz8q2vdp88'
bot = commands.Bot(command_prefix='!')

#def get_channel_list():
#	 for channel in bot.get_all_channels():
#		  yield channel.name

#channels = get_channel_list()
#print (type(channels))
#for n in channels:
#	 print(n)
current_vc = discord.VoiceClient

@bot.command(pass_context=True)  # разрешаем передавать агрументы
async def test(ctx, arg):  # создаем асинхронную фунцию бота
	await ctx.send("Go to naxui")  # отправляем обратно аргумент

@bot.command()
async def test2(ctx):
	 await ctx.send('Hello')

@bot.command()
async def test3(ctx):
	 if ctx.message.author.voice:
		 await ctx.send("You are in " + ctx.message.author.voice.channel.name)
		 current_channel = ctx.message.author.voice.channel
		 current_vc = await current_channel.connect()
		 source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('sa.mp3'))
		 current_vc.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
		 await ctx.send("s")
		 current_vc.source.volume = 100
#		 vc.is_playing()
		 current_vc.pause()
#		 vc.stop()
		 current_vc.resume()
	 else:
		 await ctx.send("no channal")

@bot.command()
async def test4(ctx):
	if ctx.message.author.voice:
		 if current_vc.is_connected():
			  await ctx.send("Disconnected...")
			  await current_vc.disconnect()
		 else:
			  await ctx.send("Client disconnected already.")
	else:
		await ctx.send("no channal")


bot.run(TOKEN)
