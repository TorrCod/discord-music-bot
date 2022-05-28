# Import Package
from logging import exception
from re import S
from turtle import done
from typing import List
import discord, youtube_dl, asyncio, tor_command, time
from discord.ext import commands
from threading import Thread

# Music Command class
class music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.queue = []

    # Play Command
    @commands.command()
    async def play(self,ctx,*,link):
        lockProc = asyncio.Lock()

        # Check the author if the author is in voice channel
        print("checking authors and channel")
        if await self.is_on_channel(ctx):
            print("somethings wrong.. -tplay command cancelled..")
            return

        async with lockProc:
            youtubePlayer = YoutubePlay(ctx.voice_client, self.queue) # Create YoutubePLay object an instance
            author = ctx.message.author.name

            # If voice_client is not playing, if true play song else add the music to queue
            if not self.queue and not ctx.voice_client.is_playing():
                print("\n Bot is not busy... attempting to proceed")
                self.queue.append({'song':link,'author': author}) # add link to queue first
                await youtubePlayer.play_music() # play the song from given link

                # if the link is playlist or url, get a list of titles and add it to queue
                if 'https://www.youtube.com/' in link:
                    titleList = await youtubePlayer.get_playlist(link)
                    self.add_queue(titleList,author) # Add list of title in queue
            
            else:
                titleList = await youtubePlayer.get_playlist(link)
                self.add_queue(titleList,author) # Add list of title in queue
                print("\n Bot is busy... queue added")

            print("\nSending embed")
            musicStatus = youtubePlayer.music_status()
            playingNow = musicStatus.get('playingNow')
            titleQueue = musicStatus.get('queue')

            print("\nPlaying Now: " + str(playingNow))
            print("\nQueue: " + str(titleQueue))

            await send_embed_playlist(ctx,playingNow,titleQueue)

            await asyncio.sleep(5)
            try:
                await ctx.message.delete() # Delete Message
            
            except:
                pass
            
        print("\nPlayer Completed\n")

    # Disconnect Command
    @commands.command()
    async def disconnect(self,ctx):
        channelName = ctx.message.channel.name

        # Check if the command is sent on main text-channel
        if channelName != "🎵tor-command":
            await self.send_error_msg(ctx,msgContent="Send that command to 🎵tor-command channel")
            return

        # Check the voice if playing
        if not ctx.voice_client.is_playing():
            await self.send_error_msg(ctx,msgContent="No Playing Sound Right Now")
            return

        await self.is_on_channel(ctx) # Check if author is on channel
        ctx.voice_client.stop() # Stop voice playing
        self.queue.clear() # Clear the queue
        await ctx.voice_client.disconnect() # disconnect the bot from channel

        try:
            await ctx.message.delete() # Delete the command 
        except:
            pass

        print("\nDISCONNECTED")   

    # Skip Command
    @commands.command()
    async def skip(self,ctx):
        channelName = ctx.message.channel.name

        # Check if the command is sent on main text-channel
        if channelName != "🎵tor-command":
            await self.send_error_msg(ctx,msgContent="Send that command to 🎵tor-command channel")
            return

        # Check the voice if playing
        if not ctx.voice_client.is_playing():
            await self.send_error_msg(ctx,msgContent="No Playing Sound Right Now")
            return

        await self.is_on_channel(ctx) # Check if author is on channel
        ctx.voice_client.stop() # Stop voice playing

        try:
            await ctx.message.delete() # Delete message
        except:
            pass

        print("\nSKIPPED\n") # Print Skip

    # Stop Command
    @commands.command()
    async def stop(self,ctx):
        channelName = ctx.message.channel.name

        # Check if the command is sent on main text-channel
        if channelName != "🎵tor-command":
            await self.send_error_msg(ctx,msgContent="Send that command to 🎵tor-command channel")
            return

        # Check the voice if playing
        if not ctx.voice_client.is_playing():
            await self.send_error_msg(ctx,msgContent="No Playing Sound Right Now")
            return

        await self.is_on_channel(ctx) # Check if author is on channel
        
        ctx.voice_client.stop() # Stop voice playing
        self.queue.clear() # Clear the queue

        try:
            await ctx.message.delete() # Delete the command 
        except:
            pass

        print("\nSTOPPED")   

    # Pause Command
    @commands.command()
    async def pause(self,ctx):
        channelName = ctx.message.channel.name

         # Check if the command is sent on main text-channel
        if channelName != "🎵tor-command":
            await self.send_error_msg(ctx,msgContent="Send that command to 🎵tor-command channel")
            return

        # Check the voice if playing
        if not ctx.voice_client.is_playing():
            await self.send_error_msg(ctx,msgContent="No Playing Sound Right Now")
            return

        await self.is_on_channel(ctx) # Check if author is on channel

        ctx.voice_client.pause() # Resume Song

        try:
            await ctx.message.delete() # Delete Message
        except:
            pass
        
        print("\nPAUSED")

    # Resume Command
    @commands.command()
    async def resume(self,ctx):
        channelName = ctx.message.channel.name

         # Check if the command is sent on main text-channel
        if channelName != "🎵tor-command":
            await self.send_error_msg(ctx,msgContent="Send that command to 🎵tor-command channel")
            return

        # Check the voice if playing
        if not ctx.voice_client.is_playing():
            await self.send_error_msg(ctx,msgContent="No Playing Sound Right Now")
            return

        await self.self.is_on_channel(ctx) # Check if author is on channel
        
        ctx.voice_client.resume() # Resume Song

        try:
            await ctx.message.delete() # Delete Message
        except:
            pass
    
        print("\nRESUMED")

    # add item to queue method
    def add_queue (self, item, author):
        for x in item:
            self.queue.append({'song':x , 'author': author})

    # Send Error Method
    async def send_error_msg(self, ctx, msgContent):
        errEmbed = discord.Embed(title=msgContent,description = "",color=0xFF0000)
        await ctx.send(embed = errEmbed, delete_after = 5)       
        
        await asyncio.sleep(5)

        try:
            await ctx.message.delete() # Delete Message
        except:
            pass

    # Is author on channel method
    async def is_on_channel(self,ctx):
        channelName = ctx.message.channel.name
        voice_channel = ctx.author.voice.channel

        # Check if the sent message is on tor-command channel
        if channelName != "🎵tor-command":
            data = ctx.message.guild.text_channels

            # if the tor-command channel is not in the discord server then create one
            if '🎵tor-command' not in [data[x].name for x in range(len(data))]:
                print("\nNot Found Music Default Channel\n")
                await tor_command.create_tor_channel(ctx.message.guild)

            # Notify author to send the command in tor-command channel
            await self.send_error_msg(ctx,msgContent="Send that command to 🎵tor-command channel")
            return True # Return True
        
        # Check author if he/she in voice channel
        if ctx.author.voice is None:
            await self.send_error_msg(ctx,msgContent="You are not in a voice channel")
            return True

        # Check if bot is connected to channel 
        # if none then connect 
        # else move to current channel
        if ctx.voice_client is None:
            await voice_channel.connect()
        else:
            await ctx.voice_client.move_to(voice_channel)

 # Declare Global variable 
 # to store the data of current playing 
current_playing = None

# Player Class
class YoutubePlay:
    def __init__(self, voice_client, yt_queue):
        self.yt_queue = yt_queue
        self.voice_client = voice_client
        self.playing_now = None

    # Return list of titles from url to be appended to yt_list
    async def get_playlist(self, url):
        YDL_OPTIONS = {
            'format':"bestaudio",
            'default_search':"auto",
            'max_downloads' : "15"
            }

        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            title = None
            title_queue = []

            if 'entries' in info:
                if len(info['entries']) > 1:
                    print("\nNumber of songs "+str(len(info['entries'])))
                    for x in range(len(info['entries'])):
                        title = info['entries'][x]['title']
                        
                        if x == 0:
                            pass
                        
                        elif x == 15:
                            break

                        else:
                            title_queue.append(title)
                
                else:
                    title = info['entries'][0]['title']
                    title_queue.append(title)
            
            elif 'formats' in info:
                title = info['title']
                title_queue.append(title)
        
        return  title_queue

    # Return the title and source of a given song name
    async def get_song(self, song_name):
        YDL_OPTIONS = {'format':"bestaudio",'default_search':"auto",'noplaylist':"True"}
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}      
        ytMusic = None
        
        # Extract info from url or searched item
        print("\n Preparing Music")
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(song_name, download=False)

            if 'entries' in info:
                ytMusic = info['entries'][0]['formats'][0]['url']
                title = info['entries'][0]['title']

            if 'formats' in info:
                ytMusic = info['formats'][0]['url']
                title = info['title']

            source = await discord.FFmpegOpusAudio.from_probe(ytMusic,**FFMPEG_OPTIONS)
        
        info = {'source': source, 'title':title}
        return info

    # Play Music
    async def play_music(self):
        # check if queue has items in it, if true play song else pass:
        if self.yt_queue:
            global current_playing
            sourceInfo = await self.get_song(self.yt_queue[0]['song'])
            print(sourceInfo)
            source = sourceInfo.get("source")
            title = sourceInfo.get("title")
            author = self.yt_queue[0]['author']
            current_playing = {'song':title,'author':author}
            self.yt_queue.pop(0)
            print("\nPreparing: " + str(title))
            print("Remaing Queue: ")

            for x in self.yt_queue:
                print(x)

            time.sleep(2)
            self.voice_client.play(source, after = lambda e:print("Player excemption: "+str(e)) if e else asyncio.run(self.play_music()))
            
        else:
            print("\nDone PLaylist")
            return None

    def music_status(self):
        global current_playing
        status = {}
        status['playingNow'] = current_playing
        status['queue'] = self.yt_queue

        return status


# Send Embed based on given parameters
# Playing Now = songs currently playing
# queue = list of titles from queue list
embedUpdate = any
async def send_embed_playlist(ctx, playingNow, queue):
    global embedUpdate
    playlistEmbed = ""

    # Deleting past embed
    if embedUpdate == any:
        pass
    else:
        try:
            await embedUpdate.delete()
        except:
            pass

    if not playingNow:
        playlistEmbed = discord.Embed(title="ON STAND BY -_-",description = "",color=0xFF0000)
   
    else:
        playlistEmbed = discord.Embed(title="Playing Now \n" + playingNow.get('song') ,description = "Requested by: " + playingNow.get('author'),color=0x00ff00)
    
    if queue:
        playlistEmbed.add_field(name="Queue", value = formatedTitle(queue),inline=False)
    
    embedUpdate = await ctx.send(embed = playlistEmbed)
    
# Format all title
def formatedTitle(queue):
    music_title = ""
   
    for x in range(len(queue)):
        music_title = music_title + queue[x]['song'] +" @"+ queue[x]['author']+"\n"
    
    return music_title



# Setup client
def setup(client):
    client.add_cog(music(client))
    