# YANDEX

from yandex_music.client import Client
from yandex_music import Album, Playlist
import discord
from discord.ext import commands
import asyncio

login_parameters = ('serheo99@yandex.ru', 'Sn32089461')


class YandexDriver(object):

    def __init__(self):
        self.client = Client()
        login, passwd = login_parameters
        self.client = Client.from_credentials(login, passwd)
        self.queueStatus = False
        self.container: Album | Playlist
        self.current_number: [int, int] | int

    def searchTrack(self, reqest) -> (str, str):
        search_result = self.client.search(reqest, type_="track")
        track = search_result.tracks.results[0]
        if track is None:
            return None
        return self.__getTrackInfo(track);

    def initAlbumFromLink(self, url) -> str:
        self.__resetQueue()
        self.current_number = [0, 0]
        #  сделать сплит урла
        self.container = self.client.albumsWithTracks(url)
        if self.container is None:
            return None
        self.queueStatus = True
        return self.container.title

    def getCurrentTrack(self) -> (str, str):
        if isinstance(self.container, Album):
            vol_num, track_num = self.current_number
            track = self.container.volumes[vol_num][track_num]
            return self.__getTrackInfo(track)
        if isinstance(self.container, Playlist):
            track = self.container.tracks[self.current_number].track
            return self.__getTrackInfo(track)

    def getNextTrack(self) -> (str, str):
        if isinstance(self.container, Album):
            vol_num, track_num = self.current_number
            if track_num + 1 == len(self.container.volumes[vol_num]):
                self.current_number[1] = 0
                if vol_num + 1 == len(self.container.volumes):
                    self.__resetQueue()
                    return
                self.current_number[0] += 1
            else:
                self.current_number[1] += 1
                track = self.container.volumes[self.current_number[0]][self.current_number[1]]
                return self.__getTrackInfo(track)
        if isinstance(self.container, Playlist):
            if self.current_number + 1 == len(self.container.tracks):
                self.__resetQueue()
                return
            self.current_number + 1
            track = self.container.tracks[self.current_number].track
            return self.__getTrackInfo(track)

    def __getTrackInfo(self, track) -> (str, str):
        list_of_DI = track.getDownloadInfo(True)
        info_string = "%s -- %s -- %s " % (track.title, track.artists[0].name, track.albums[0].title)
        link = None
        for info in list_of_DI:
            if info.codec == "mp3" and info.bitrate_in_kbps == 192:
                link = info.getDirectLink()
                break
        return info_string, link

    def __resetQueue(self):
        self.container = None
        self.current_number = 0
        self.queueStatus = False


# DISCORD


yDriver = YandexDriver()
# yDriver.getAlbumFromLink("9823194")

TOKEN = 'Njc2NDU5NDQ1Nzc3MDcyMTMx.XkPngQ.tvpRDqztbDBESGgIxXz8q2vdp88'
bot = commands.Bot(command_prefix='!')


class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.play_ctx = None

    @commands.command(pass_context=True)
    async def play(self, ctx, *, arg):
        await ctx.send("Search: \"%s\"... " % (arg))
        track = yDriver.searchTrack(arg)
        if track == None:
            await ctx.send("Track not found!")
            return
        await self.__playTrack(ctx, track)

    @commands.command(pass_context=True)
    async def play_album(self, ctx, *, arg):
        await ctx.send("Search: \"%s\"..." % (arg))
        album_name = yDriver.initAlbumFromLink(arg)
        if not yDriver.queueStatus:
            await ctx.send("Album not found!")
            return
        await ctx.send("Found: %s" % (album_name))
        track = yDriver.getCurrentTrack()
        await self.__playTrack(ctx, track)

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
    @play_album.before_invoke
    async def ensure_voice(self, ctx):
        self.play_ctx = ctx
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

    async def __playTrack(self, ctx, track):
        info_string, url = track
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url))
        ctx.voice_client.play(source, after=self.__after_track)
        await ctx.send('Now playing: ' + info_string)

    def __after_track(self, error):
        print("after")
        f_send = self.play_ctx.send("Player error: %s" % error)
        track = yDriver.getNextTrack()
        f_play = self.__playTrack(self.play_ctx, track)
        f_sendt = asyncio.run_coroutine_threadsafe(f_send, self.bot.loop)
        f_playt = asyncio.run_coroutine_threadsafe(f_play, self.bot.loop)
        try:
            if error is not None:
                f_sendt.result()
                return
            if not yDriver.queueStatus:
                return
            f_playt.result()
        except:
            print("__afterTrack error")
            pass


bot.add_cog(Music(bot))
bot.run(TOKEN)
