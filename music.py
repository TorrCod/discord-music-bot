# Import Discord Package
import discord, youtube_dl, asyncio, tor_command
from discord.ext import commands
# Youtube Queue
embedUpdate = any
torSongTitle = []
torPlayingNow = []
is_playing = False
lockProc = asyncio.Lock()
# Music Command class
class music(commands.Cog):
    def __init__(self, client):
        self.client = client
    # Play Command
    @commands.command()
    async def play(self,ctx,*,url):
        global is_playing
        # Check the author if the author is in voice channel
        if await is_on_channel(ctx):
            return
        if not is_playing:
            is_playing = True
            # Add song to queue
            async with lockProc:
                await play_yt_music(ctx,url,False)
                await get_youtube_title(ctx,url)
            await on_playing(ctx)
            try: 
                torSongTitle.pop(0)
            except:
                pass
            while torSongTitle:
                await play_yt_music(ctx,torSongTitle[0]['title'],True)
            is_playing = False
            await send_embed_playlist(ctx)
        else:
            async with lockProc:
                await get_youtube_title(ctx,url)
    # Disconnect Command
    @commands.command()
    async def disconnect(self,ctx):
        global is_playing
        channelName = ctx.message.channel.name
        if channelName != "🎵tor-command":
            await ctx.send("Send that command to 🎵tor-command channel")
            return
        # Check the author if the author is in voice channel
        if not is_playing:
            await ctx.send("No Playing Sound Right Now")
            return
        await is_on_channel(ctx)
        ctx.voice_client.stop()
        torSongTitle.clear()
        await ctx.voice_client.disconnect()
        try:
            await ctx.message.delete()
        except:
            pass
        is_playing = False
        print("\nDISCONNECTED")   
    # Skip Command
    @commands.command()
    async def skip(self,ctx):
        channelName = ctx.message.channel.name
        if channelName != "🎵tor-command":
            await ctx.send("Send that command to 🎵tor-command channel")
            return
        # Check the author if the author is in voice channel
        if not is_playing:
            await ctx.send("No Playing Sound Right Now")
            return
        await is_on_channel(ctx)
        print("\nSKIPPED\n")
        ctx.voice_client.stop()
        try:
            await ctx.message.delete()
        except:
            pass
    # Stop Command
    @commands.command()
    async def stop(self,ctx):
        global is_playing
        channelName = ctx.message.channel.name
        if channelName != "🎵tor-command":
            await ctx.send("Send that command to 🎵tor-command channel")
            return
        # Check the author if the author is in voice channel
        if not is_playing:
            await ctx.send("No Playing Sound Right Now")
            return
        await is_on_channel(ctx)
        torSongTitle.clear()
        ctx.voice_client.stop()
        print("\nSTOPED")
        try:
            await ctx.message.delete()
        except:
            pass
        is_playing = False
    # Pause Command
    @commands.command()
    async def pause(self,ctx):
        channelName = ctx.message.channel.name
        if channelName != "🎵tor-command":
            await ctx.send("Send that command to 🎵tor-command channel")
            return
        # Check the author if the author is in voice channel
        if not is_playing:
            await ctx.send("No Playing Sound Right Now")
            return
        await is_on_channel(ctx)
        ctx.voice_client.pause()
        print("\nPAUSED")
        try:
            await ctx.message.delete()
        except:
            pass
    # Resume Command
    @commands.command()
    async def resume(self,ctx):
        channelName = ctx.message.channel.name
        if channelName != "🎵tor-command":
            await ctx.send("Send that command to 🎵tor-command channel")
            return  
        # Check the author if the author is in voice channel
        if not is_playing:
            await ctx.send("No Playing Sound Right Now")
            return
        await is_on_channel(ctx)
        ctx.voice_client.resume()
        print("\nRESUMED")
        try:
            await ctx.message.delete()
        except:
            pass
        
# Is author on channel function
async def is_on_channel(ctx):
    channelName = ctx.message.channel.name
    if channelName != "🎵tor-command":
        data = ctx.message.guild.text_channels
        if '🎵tor-command' not in [data[x].name for x in range(len(data))]:
            print("\nNot Found Music Default Channel\n")
            await tor_command.create_tor_channel(ctx.message.guild)
        await ctx.send("Send that command to 🎵tor-command channel")
        return True
    if ctx.author.voice is None:
        await ctx.send("You are not in a voice channel")
        return True
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await voice_channel.connect()
    else:
        await ctx.voice_client.move_to(voice_channel)

async def get_youtube_title(ctx,link):
    YDL_OPTIONS = {'format':"bestaudio",'default_search':"auto"}
    author = ctx.message.author.name
    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(link, download=False)
        title = ""
        if 'entries' in info:
            print("Getting Entries")
            numberOfSong = len(info['entries'])
            for x in range(numberOfSong):
                if x == 15:
                    break
                else:
                    title = info['entries'][x]['title']
                    torSongTitle.append({"title":title,"author":author})
        elif 'formats' in info:
            print("Getting Formats")
            title = info['formats'][0]['title']
            torSongTitle.append({"title":title,"author":author})

    print("\nGetting Youtube Title:")
    print(torSongTitle)
    # Send Embed Message
    await send_embed_playlist (ctx)

async def play_yt_music(ctx,title,on_play):
    YDL_OPTIONS = {'format':"bestaudio",'default_search':"auto",'noplaylist':"True"}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    vc = ctx.voice_client
    # Add music to playlist
    print("\n Preparing Music")
    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(title, download=False)
        if 'entries' in info:
            url2 = info['entries'][0]['formats'][0]['url']
            title = info['entries'][0]['title']
            source = await discord.FFmpegOpusAudio.from_probe(url2,**FFMPEG_OPTIONS)
        elif 'formats' in info:
            url2 = info['formats'][0]['url']
            title = info['title']
            source = await discord.FFmpegOpusAudio.from_probe(url2,**FFMPEG_OPTIONS)
        await asyncio.sleep(3)
        vc.play(source)
        
    print("\n---- PLAYING Now ---- \n" + title + "\n")
    if on_play:
        await send_embed_playlist(ctx)
        await on_playing(ctx)
        print("\n --- Finished Playing ----\n")
        try:
            torSongTitle.pop(0)
        except:
            pass
        
    
# On_Playing
async def on_playing(ctx):
    vc = ctx.voice_client
    on_playing = False
    while not on_playing:
        if vc.is_playing() or vc.is_paused():
            while vc.is_playing() or vc.is_paused():
                await asyncio.sleep(5)
            on_playing = True
            break
        await asyncio.sleep(5)
# Send Embed
async def send_embed_playlist(ctx):
    global embedUpdate
    playlistEmbed = ""
    try:
        await ctx.message.delete()
    except:
        pass
    # Deleting past embed
    if embedUpdate == any:
        pass
    else:
        try:
            await embedUpdate.delete()
        except:
            pass
    if not torSongTitle:
        playlistEmbed = discord.Embed(title="NO CURRENTLY PLAYING SONGS RIGHT NOW",description = "",color=0xFF0000)
    else:
        playlistEmbed = discord.Embed(title="Playing Now \n"+torSongTitle[0]['title'],description = "Requested by: " + torSongTitle[0]['author'],color=0x00ff00)
        if len(torSongTitle) > 1:
            playlistEmbed.add_field(name="Queue", value = formatedTitle(),inline=False)
    embedUpdate = await ctx.send(embed = playlistEmbed)
    
# Format all title
def formatedTitle():
    music_title = ""
    for x in range(len(torSongTitle)):
        if x == 0:
            pass
        else:
            music_title = music_title + torSongTitle[x]['title'] +" @"+ torSongTitle[0]['author'] +"\n"
    return music_title
# Setup client
def setup(client):
    client.add_cog(music(client))
    