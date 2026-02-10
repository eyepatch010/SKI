# utils/logger.py
import discord
class _Logger:
    def __init__(self):
        self.client = None  # will be set once during initialization


    def init(self, client):
        """Call this ONCE in main.py after client is created."""
        self.client = client

    async def send_log(self, message: str):
        if not self.client:
            raise RuntimeError("Logger not initialized with a client!")
        
        log_channel = self.client.get_channel(1432312668911567028)  # Replace with your ID
        if log_channel:
            await log_channel.send(message)
        else:
            print("Log channel not found")


    async def send_command_log(self,command_name:str,user:discord.User,extraContent:str=""):
        log_channel = self.client.get_channel(1432312668911567028)
        if log_channel:
            embed=discord.Embed(title=command_name,description=extraContent,color=discord.Color.blue())
            embed.set_author(name=f"{user}",icon_url=user.display_avatar.url)
            await log_channel.send(embed=embed)
        else:
            print("Log channel not found")
        

# Create a global logger instance that can be imported anywhere
Logger = _Logger()
