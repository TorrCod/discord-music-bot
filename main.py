# Import Discord Package
import asyncio
import discord, music, time, _privVariables ,tor_command
from discord.ext import commands

# Client
client = commands.Bot(command_prefix='-t', intents = discord.Intents.all())

#variables
try:
    bot_token = _privVariables.tokken
except:
    print("Put your own bot tokken in bot_tokken variable")

# Startup Bot
@client.event
async def on_ready():
    print("\nTorR BOT READY\n")

@client.event
async def on_guild_join(guild):
    await tor_command.create_tor_channel(guild)

# Music Command                 
cogs = [music]
for i in range(len(cogs)):
    cogs[i].setup(client)

# Help Command
@client.command(name='helpme')
async def helpme(ctx):
    await ctx.send("Tulong Amp! kalma ka wait ..")
    await asyncio.sleep(2)
    await ctx.send("\nETO COMMAND KO "+
                    "\ntorplay 'paste URL right here' - patutog ng music"+ 
                    "\ntorpause - pause yung music"+
                    "\ntorresume - resume yung music"+
                    "\ntordisconnect - disconnect ako dyan sa channel aports")


# Run the client on the server
client.run(bot_token)