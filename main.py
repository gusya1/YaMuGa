

##client = Client()
##client = Client.from_credentials('serheo99@yandex.ru', 'Sn32089461')
##client.users_likes_tracks()[0].track.download('example.mp3')



#YANDEX

from yandex_music.client import Client
from yandex_music import Search, SearchResult


client = Client()
client = Client.from_credentials('serheo99@yandex.ru', 'Sn32089461')
#search_request_id = 'myt1-0261-c2e-msk-myt-music-st-e72-18274.gencfg-c.yandex.net-1573323135801461' \
#                        '-3742331365077765411-1573323135819 '
#text = 'NCS'
#misspell_corrected = False
#nocorrect = False
#best = Best(None, None)
#albums = SearchResult(None, None, None, None, None)
#artists = SearchResult(None, None, None, None, None)
#playlists = SearchResult(None, None, None, None, None)
#tracks = SearchResult(None, None, None, None, None)
#videos = SearchResult(None, None, None, None, None)
#Search(search_request_id, text, best, albums, artists, playlists, tracks, videos, misspell_corrected, nocorrect, client)
search_reqest = client.search("рив гош")
print(search_reqest.best.result.title)
print(search_reqest.best.result.getDownloadInfo(True))
link = search_reqest.best.result.getDownloadInfo(True)[0].getDirectLink()
#search_reqest.best.result.download('example.mp3')

#DISCORD

import discord
from discord.ext import commands

TOKEN = 'Njc2NDU5NDQ1Nzc3MDcyMTMx.XkPngQ.tvpRDqztbDBESGgIxXz8q2vdp88'
bot = commands.Bot(command_prefix='!')

#@bot.command(pass_context=True)  # разрешаем передавать агрументы
#async def test(ctx, arg):  # создаем асинхронную фунцию бота
#	await ctx.send("Go to naxui")  # отправляем обратно аргумент

class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def play(self, ctx):
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(link))
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
        await ctx.send('Now playing: Still Alive OST')

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








