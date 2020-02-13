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

#@bot.command(pass_context=True)  # разрешаем передавать агрументы
#async def test(ctx, arg):  # создаем асинхронную фунцию бота
#	await ctx.send("Go to naxui")  # отправляем обратно аргумент

#@bot.command()
#async def test2(ctx):
#	 await ctx.send('Hello')

#@bot.command()
#async def test3(ctx):
#	 if ctx.message.author.voice:
#		 await ctx.send("You are in " + ctx.message.author.voice.channel.name)
#		 current_channel = ctx.message.author.voice.channel
#		 current_vc = await current_channel.connect()
#		 source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('sa.mp3'))
#		 current_vc.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
#		 await ctx.send("s")
#		 current_vc.source.volume = 100
##		 vc.is_playing()
##		 current_vc.pause()
##		 vc.stop()
##		 current_vc.resume()
#	 else:
#		 await ctx.send("no channal")

#@bot.command()
#async def test4(self, ctx):
#		  await current_vc.disconnect()


class Music(commands.Cog):


	 def __init__(self, bot):
		 self.bot = bot

	 @commands.command()
	 async def join(self, ctx, *, channel: discord.VoiceChannel):
		 """Joins a voice channel"""

		 if ctx.voice_client is not None:
			 return await ctx.voice_client.move_to(channel)

		 await channel.connect()

	 @commands.command()
	 async def play(self, ctx):
		 """Plays a file from the local filesystem"""

		 source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("sa.mp3"))
		 ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

		 await ctx.send('Now playing: {}'.format(query))

#	 @commands.command()
#	 async def yt(self, ctx, *, url):
#		 """Plays from a url (almost anything youtube_dl supports)"""

#		 async with ctx.typing():
#			 player = await YTDLSource.from_url(url, loop=self.bot.loop)
#			 ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

#		 await ctx.send('Now playing: {}'.format(player.title))

#	 @commands.command()
#	 async def stream(self, ctx, *, url):
#		 """Streams from a url (same as yt, but doesn't predownload)"""

#		 async with ctx.typing():
#			 player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
#			 ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

#		 await ctx.send('Now playing: {}'.format(player.title))

	 @commands.command()
	 async def volume(self, ctx, volume: int):
		 """Changes the player's volume"""

		 if ctx.voice_client is None:
			 return await ctx.send("Not connected to a voice channel.")

		 ctx.voice_client.source.volume = volume / 100
		 await ctx.send("Changed volume to {}%".format(volume))

	 @commands.command()
	 async def stop(self, ctx):
		 """Stops and disconnects the bot from voice"""

		 await ctx.voice_client.disconnect()

	 @play.before_invoke
#	 @yt.before_invoke
#	 @stream.before_invoke
	 async def ensure_voice(self, ctx):
		 if ctx.voice_client is None:
			 if ctx.author.voice:
				 await ctx.author.voice.channel.connect()
			 else:
				 await ctx.send("You are not connected to a voice channel.")
				 raise commands.CommandError("Author not connected to a voice channel.")
		 elif ctx.voice_client.is_playing():
			 ctx.voice_client.stop()

bot.add_cog(Music(bot))
bot.run(TOKEN)
