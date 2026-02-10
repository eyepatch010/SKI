

import requests
from bs4 import BeautifulSoup
import discord
import os

import asyncio
#import undetected_chromedriver as uc
from discord.ext import commands, tasks
from collections import OrderedDict
from jishaku.codeblocks import codeblock_converter


from db.dbutil import get_mongoDb
from db.dbclient import MongoDBClient
from utils.logger import Logger
from sekaiInformer.settings import settings
#import pyNacl

IDS = [574795956818673674,523593147004223488]  # Replace with your Discord ID

def owner_check(interaction: discord.Interaction) -> bool:
    return interaction.user.id in IDS






# Set up bot
intents = discord.Intents.all()
#1349756331761860639  # Allow message reading
activity = discord.Activity(type=discord.ActivityType.listening, name="discord.gg/wonderhoy")

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='=',intents=intents)
        self.initial_extensions = [
            'cogs.shows',
            'cogs.score_stats',
            'cogs.message_utility'
        ]
    async def setup_hook(self):
        mongodb=await get_mongoDb()
        self.mongodb=mongodb
        self.IDS=IDS
        for ext in self.initial_extensions:
            await self.load_extension(ext)
        Logger.init(client)


        await self.load_extension('jishaku')
        os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
        os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
        os.environ["JISHAKU_HIDE"] = "True"
        await self.reload_extension('jishaku')



        try:
            synced = await self.tree.sync()  # Sync commands with Discord
            print(f"Synced {len(synced)} commands.")
        except Exception as e:
            print(f"Error syncing commands: {e}")

                


   
    """async def close(self):
        await super().close()
        await self.session.close()"""

    async def on_ready(self):
        global activity
        global ErrorChannel
        ErrorChannel=client.get_channel(1350863748604231720)
        await self.change_presence(status=discord.Status.idle, activity=activity)
        print(f"✅ Logged in as {self.user}")


#client = commands.Bot(command_prefix="=", intents=intents)
client=Bot()


client.add_tree()

@client.tree.error
async def global_error(interaction: discord.Interaction, error):
    
    try:
        await interaction.response.send_message(content=f"An error occurred", ephemeral=True)
    except:
        await interaction.followup.send(content=f"An error occurred", ephemeral=True)
    #await ErrorChannel.send(f"Error: {error}")
    raise error
from ui.UIshow import ShowDisplay
from Schemas.settingSchema import ShowChannelConnections


    
@client.event
async def on_message(message):
    #print("on message")
    if message.author == client.user:
        return    
    if isinstance(message.channel, discord.DMChannel) and message.author != client.user:
        serverch = client.get_channel(1410721348090724454)
        await serverch.send(content=f"`-> DM from {message.author}:` {message.content}\n`User Id:` {message.author.id}\n")
    await client.process_commands(message)


@client.command()
@commands.is_owner()
async def ev2(ctx, *, arg):
    cog = client.get_cog("Jishaku")
    res = codeblock_converter(arg+"\n"+"return")
    await cog.jsk_python(ctx, argument=res)


token=settings.CLIENT_TOKEN    
client.run(token)


