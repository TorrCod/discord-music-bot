import discord
from discord.ext import commands

channelEmbed = any
client = discord.Client(intents = discord.Intents.all())
async def create_tor_channel(guild):
    torBotCategory = await guild.create_category(name='TORR MUSIC BOT', position= 0)
    torBotChannel = await guild.create_text_channel(name='🎵tor-command',category= torBotCategory)
    myEmbed = discord.Embed(title = "Command List", description = "Sariling music custom Bot ng server lesG", color = 0x00ff00, url='https://image.shutterstock.com/image-vector/hand-gesture-fuck-you-symbol-260nw-587857943.jpg')
    myEmbed.set_author(name="Torrrrzz")
    myEmbed.add_field(name="-tplay youtube title / URL", value="Play Music sa YT\n   Halimbawa\n   -tplay https://www.youtube.com/watch?v=o8cXBCABacs\n   O kaya\n   -tplay sun and moon",inline=False)
    myEmbed.add_field(name="-tpause", value="Pause the music",inline=False)
    myEmbed.add_field(name="-tresume", value="Resume the music",inline=False)
    myEmbed.add_field(name="-tskip", value="Skip current music",inline=False)
    myEmbed.add_field(name="-tstop", value="Stop TorBot from playing",inline=False)
    myEmbed.add_field(name="-tdisconnect", value="Disconnect TorBot to channel",inline=False)
    myEmbed.add_field(name="-thelp", value="MEKMEK",inline=False)
    myEmbed.set_footer(text="Ahmm Goodluck mga kups")
    await torBotChannel.send(embed = myEmbed)
