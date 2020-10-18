from discord import Activity
from bot.yandex_handler import YandexDriver
from bot.queue_containers import ContainersQueue
# import discord_logger
from bot.discord_logger import logger
import discord
from discord.ext import commands
import asyncio
import json
# import bot.yandex_handler as yh

# DISCORD

container_queue = ContainersQueue()

TOKEN = ""
USERNAME = ""
PASSWORD = ""

try:
    auch_file = open("auch.json", "r")
    json_doc = json.load(auch_file)
    TOKEN = json_doc["token"]
    USERNAME = json_doc["y_username"]
    PASSWORD = json_doc["y_password"]
except Exception as e:
    logger.error("Load auch error: %s" % e)
    exit(1)


yDriver = YandexDriver(USERNAME, PASSWORD)
start_activity: Activity = discord.Activity(name="!help", type=discord.ActivityType.listening)

description = """Welcome to PreAlfa version 0.1.1 YaMuGa Bot!"""

bot = commands.Bot(command_prefix='!', activity=start_activity, description=description)


@bot.event
async def on_ready():
    logger.info("Log in! Username: %s  ID: %s" % (bot.user.name, bot.user.id))


# @bot.event
# async def on_error(event, *args, **kwargs):
#     logger.warning("on_error")


class Music(commands.Cog):

    def __init__(self, discord_bot):
        self.bot = discord_bot
        self.play_ctx = None
        self.next_track_after = True

    async def cog_command_error(self, ctx, error):
        logger.error('In "%s" command error occurred: %s' % (ctx.command, error))
        await ctx.send("I can't execute the command: %s" % error)

    @commands.command(pass_context=True)
    async def change_prefix(self, ctx, prefix):
        """Changes the prefix to a custom one. \nUsage: <prefix>change_prefix <custom prefix>"""
        try:
            logger.warning("change_prefix")
            if prefix == "":
                raise commands.CommandError("Prefix cannot be empty.")
            bot.command_prefix = prefix
            activity = discord.Activity(name="%shelp" % prefix, type=discord.ActivityType.listening)
            await bot.change_presence(activity=activity)
            await ctx.send("Prefix changed to \"%s\"" % prefix)
        except Exception:
            logger.error(ctx, "Exception occurred: ")

    @commands.command(pass_context=True)
    async def play(self, ctx, *, arg):
        """Play track from search. Usage: <prefix>play <search request>"""
        await ctx.send("Search: \"%s\"... " % arg)
        container = yDriver.get_track_from_search(arg)
        if container is None:
            raise commands.CommandError("Track not found!")
        container_queue.clear()
        container_queue.append_container(container)
        track = container_queue.next_track()
        if track is None:
            raise commands.CommandError("Cannot load track!")
        await self.__play_track(ctx, track)

    @commands.command(pass_context=True)
    async def play_album(self, ctx, *, arg):
        """Play album from URL. Usage: <prefix>play_album <URL>"""
        await ctx.send("Search: \"%s\"..." % arg)
        container = yDriver.get_album_from_link(arg)
        if container is None:
            raise commands.CommandError("Album not found!")
        container_queue.clear()
        container_queue.append_container(container)
        track = container_queue.next_track()
        if track is None:
            raise commands.CommandError("Cannot load track!")
        await self.__play_track(ctx, track)

    @commands.command(pass_context=True)
    async def play_playlist(self, ctx, *, arg):
        """Play playlist from URL. Usage: <prefix>play_playlist <URL>"""
        await ctx.send("Search: \"%s\"..." % arg)
        container = yDriver.get_playlist_from_link(arg)
        if container is None:
            raise commands.CommandError("Playlist not found!")
        container_queue.clear()
        container_queue.append_container(container)
        track = container_queue.next_track()
        if track is None:
            raise commands.CommandError("Cannot load track!")
        await self.__play_track(ctx, track)

    @commands.command()
    async def next(self, ctx):
        """Play next track"""
        self.next_track_after = False
        track = container_queue.next_track()
        if track is None:
            await ctx.send("The queue is over")
            return
        await self.__play_track(ctx, track)
        self.next_track_after = True

    @commands.command()
    async def prev(self, ctx):
        """Play prev track"""
        self.next_track_after = False
        track = container_queue.prev_track()
        if track is None:
            await ctx.send("The queue is over")
            return
        await self.__play_track(ctx, track)
        self.next_track_after = True

    @commands.command()
    async def pause(self, ctx):
        """Pause player"""
        vc = ctx.voice_client
        if vc:
            if vc.is_connected() and vc.is_playing():
                vc.pause()
                return
        await ctx.send("Nothing is playing now")

    @commands.command()
    async def resume(self, ctx):
        """Resume player"""
        vc = ctx.voice_client
        if vc:
            if vc.is_paused():
                vc.resume()
            else:
                await ctx.send("I already paused")
        else:
            await ctx.send("I don't work anyway")

    @commands.command()
    async def clear_queue(self, ctx):
        """Clear queue"""
        container_queue.clear()
        vc = ctx.voice_client
        if vc:
            if vc.is_connected():
                vc.stop()
        await ctx.send("The queue cleared")

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume. Usage: <prefix>volume <0-100>"""
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
    @prev.before_invoke
    @next.before_invoke
    async def ensure_voice(self, ctx):
        self.play_ctx = ctx
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

    def meth(self):
        return "mp3", "192"

    async def __play_track(self, ctx, track):
        info_string, url = track
        # TODO попробовать сначала загружать на диск, а потом воспроизводить
        source = await discord.FFmpegOpusAudio.from_probe(url, method=self.meth)
        # source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url, options=""))
        ctx.voice_client.play(source, after=self.__after_track)
        await ctx.send('Now playing: ' + info_string)

    def __after_track(self, error):
        track = None
        if self.next_track_after:
            track = container_queue.next_track()
        try:
            if error is not None:
                logger.error("Player error: %s" % error)
                return
            if track is None:
                return
            f_play = self.__play_track(self.play_ctx, track)
            f_playt = asyncio.run_coroutine_threadsafe(f_play, self.bot.loop)
            f_playt.result()
        except Exception:
            logger.exception("__afterTrack error:")
            pass


try:
    bot.add_cog(Music(bot))
    bot.run(TOKEN)
except discord.LoginFailure as e:
    logger.error("Discord login: %s" % e)

