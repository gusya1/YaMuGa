# YANDEX


from yandex_handler import YandexDriver
from queue_containers import ContainersQueue
import discord
from discord.ext import commands
import asyncio

# DISCORD


yDriver = YandexDriver()
container_queue = ContainersQueue()
# container = yDriver.get_track_from_search("влюблённый металлист").container
# for dinfo in container.getDownloadInfo():
#     print("%s %d" % (dinfo.codec, dinfo.bitrate_in_kbps))

token_file = open("token", "r")
TOKEN = token_file.read()

activity = discord.Activity(name="!help", type=discord.ActivityType.listening)

description = """Welcome to PrePrePreAlfa version 0.0.0.0.0.0.99 YaMuGa Bot!"""

bot = commands.Bot(command_prefix='!', activity=activity, description=description)


@bot.event
async def on_ready():
    print("Log in!")
    print("Username: %s" % bot.user.name)
    print('ID: %s' % bot.user.id)


class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.play_ctx = None

    @commands.command(pass_context=True)
    async def play(self, ctx, *, arg):
        """Play track from search. Usage: !play <search request>"""
        await ctx.send("Search: \"%s\"... " % arg)
        container = yDriver.get_track_from_search(arg)
        if container is None:
            await ctx.send("Track not found!")
            return
        container_queue.clear()
        container_queue.append_container(container)
        track = container_queue.next_track()
        if track is None:
            await ctx.send("Cannot load track!")
            return
        await self.__playTrack(ctx, track)

    @commands.command(pass_context=True)
    async def play_album(self, ctx, *, arg):
        """Play album from URL. Usage: !play_album <URL>"""
        await ctx.send("Search: \"%s\"..." % arg)
        container = yDriver.get_album_from_link(arg)
        if container is None:
            await ctx.send("Album not found!")
            return
        container_queue.clear()
        container_queue.append_container(container)
        track = container_queue.next_track()
        if track is None:
            await ctx.send("Cannot load track!")
            return
        await self.__playTrack(ctx, track)

    @commands.command(pass_context=True)
    async def play_playlist(self, ctx, *, arg):
        """Play playlist from URL. Usage: !play_playlist <URL>"""
        await ctx.send("Search: \"%s\"..." % arg)
        container = yDriver.get_playlist_from_link(arg)
        if container is None:
            await ctx.send("Playlist not found!")
            return
        container_queue.clear()
        container_queue.append_container(container)
        track = container_queue.next_track()
        if track is None:
            await ctx.send("Cannot load track!")
            return
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
        """Changes the player's volume. Usage: !volume <0-100>"""
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
    @play_playlist.before_invoke
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
        # TODO попробовать сначала загружать на диск, а потом воспроизводить
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url, options="-b:a 2000M"))
        ctx.voice_client.play(source, after=self.__after_track)
        await ctx.send('Now playing: ' + info_string)

    def __after_track(self, error):
        track = container_queue.next_track()
        try:
            if error is not None:
                f_send = self.play_ctx.send("Player error: %s" % error)
                f_sendt = asyncio.run_coroutine_threadsafe(f_send, self.bot.loop)
                f_sendt.result()
                return
            if track is None:
                return
            f_play = self.__playTrack(self.play_ctx, track)
            f_playt = asyncio.run_coroutine_threadsafe(f_play, self.bot.loop)
            f_playt.result()
        except:
            print("__afterTrack error")
            pass


bot.add_cog(Music(bot))
bot.run(TOKEN)
