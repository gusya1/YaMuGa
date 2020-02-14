##client = Client()
##client = Client.from_credentials('serheo99@yandex.ru', 'Sn32089461')
##client.users_likes_tracks()[0].track.download('example.mp3')

#YANDEX
from yandex_music.client import Client
from yandex_music import Search, SearchResult
#search_reqest = client.search("рив гош")
#print(search_reqest.best.result.title)
#print(search_reqest.best.result.getDownloadInfo(True))
#link = search_reqest.best.result.getDownloadInfo(True)[0].getDirectLink()
##search_reqest.best.result.download('example.mp3')
class YandexDriver(object):
    def __init__(self):
        self.client = Client()
        self.client = Client.from_credentials('serheo99@yandex.ru', 'Sn32089461')
    def searchTrack(self, reqest) -> (str, str):
        search_result = self.client.search(reqest, type_="track")
        track = search_result.tracks.results[0]
        if track == None:
            return None
        title = track.title
        album = track.albums[0].title
        artist = track.artists[0].name
        info_string = "%s -- %s -- %s"%(title, artist, album)
        link = ""
        list_of_DI = track.getDownloadInfo(True)
        for info in list_of_DI:
            if info.codec == "mp3" and info.bitrate_in_kbps == 192:
                link = info.getDirectLink()
                break
        return (info_string, link)
#    def getAlbum(self, url) -> [(str, str)]:
#        search_result = client.albumsWithTracks(
#        track = search_result.tracks.results[0]
#        if track == None:
#            return None
#        title = track.title
#        album = track.albums[0].title
#        artist = track.artists[0].name
#        info_string = "%s -- %s -- %s"%(title, artist, album)
#        link = ""
#        list_of_DI = track.getDownloadInfo(True)
#        for info in list_of_DI:
#            if info.codec == "mp3" and info.bitrate_in_kbps == 192:
#                link = info.getDirectLink()
#                break
#        return (info_string, link)


#DISCORD
yDriver = YandexDriver()

#class MusicQueue(object)
#    def __init__(self):
#        self.__queue : [(str, str)] = []
#        self.current : int = 0
#    def clear(self):
#        __queue.clear()
#    def append(track : (str, str)):
#        __queue.append(track)
#    def next

#    def
import discord
from discord.ext import commands
TOKEN = 'Njc2NDU5NDQ1Nzc3MDcyMTMx.XkPngQ.tvpRDqztbDBESGgIxXz8q2vdp88'
bot = commands.Bot(command_prefix='!')
#@bot.command(pass_context=True)  # разрешаем передавать агрументы
#async def test(ctx, arg):  # создаем асинхронную фунцию бота
#    await ctx.send("Go to ...")  # отправляем обратно аргумент
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command(pass_context=True)
    async def play(self, ctx, *, arg):
        await ctx.send("Search: \"%s\"..."%(arg))
        track = yDriver.searchTrack(arg)
        if track == None:
            await ctx.send("Track not found!")
            return
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(track[1]))
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
        await ctx.send('Now playing: ' + track[0])

#    @commands.command(pass_context=True)
#    async def play_album(self, ctx, *, arg):
#        await ctx.send("Search: \"%s\"..."%(arg))
#        track = yDriver.searchTrack(arg)
#        if track == None:
#            await ctx.send("Track not found!")
#            return
#        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(track[1]))
#        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
#        await ctx.send('Now playing: ' + track[0])
    @commands.command()
    async def pause(self, ctx):
        """Pause player"""
        vc = ctx.voice_client
        if vc:
            if vc.is_connected() and vc.is_playing():
                vc.pause();
                return
        await ctx.send("Nothing is playing now")
    @commands.command()
    async def resume(self, ctx):
        """Resume player"""
        vc = ctx.voice_client
        if vc:
            if vc.is_paused():
                vc.resume();
            else:
                await ctx.send("I already paused")
        else:
            await ctx.send("I don't work anyway")

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


С уважением,
Сергей Никифоров
