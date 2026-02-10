import discord
from discord import app_commands
from discord.ext import commands
from datetime import timedelta
from utils.logger import Logger
IDS = [574795956818673674,523593147004223488] 

def owner_check(interaction: discord.Interaction) -> bool:
        return interaction.user.id in IDS


class MessageUtility(commands.Cog):
    def __init__(self, client: discord.Client):
        self.client:commands.Bot = client
        self.IDS=client.IDS
        
        

    
 

    @app_commands.command(name="dm", description="Send a DM to a user")
    @app_commands.default_permissions(administrator=True)
    @app_commands.check(owner_check)
    @app_commands.describe(user="The user to DM", message="The message to send")
    async def dm(self,interaction: discord.Interaction, user: discord.User, message: str):
        try:
            await user.send(message)
            serverch = self.client.get_channel(1410721348090724454)
            await serverch.send(content=f"`<- DMed {user}:` {message}\n```User Id: {user.id}\nMessage author: {interaction.user} ```")
            await interaction.response.send_message(f"Sent DM to {user.mention}", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("I can't DM that user.", ephemeral=True)

    
    @app_commands.command(name="channel_message", description="channel Message Camu exclusive")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.check(owner_check)
    async def cm(self,interaction:discord.Interaction,*,message:str):
        u=interaction.user
        command_name=interaction.command.name
        await interaction.response.send_message(content="Request Updated",ephemeral=True)
        await interaction.channel.send(content=message)
        await Logger.send_command_log(command_name=command_name,user=u,extraContent=message)



    @app_commands.command(name="report-bug", description="Report a bug in the bot")
    @app_commands.describe(report_title="The title of the bug report", bug_description="A description of the bug")
    async def report_bug(self,interaction: discord.Interaction, report_title:str, bug_description: str):
        # Here you would handle the bug report, e.g., log it or send it to a specific channel
        bug_report_channel = self.client.get_channel(1343113281870630922)  # Replace with your bug report channel ID
        embed=discord.Embed(
            title=report_title,
            description=bug_description,
            color=discord.Color.red()
        )
        avatar_url = interaction.user.display_avatar.url
        embed.set_author( name=interaction.user.name, icon_url=avatar_url)
        embed.set_footer(text=f"Reported by {interaction.user.name} ({interaction.user.id})")
        await bug_report_channel.send(embed=embed)
        await interaction.response.send_message("Thank you for your report! We'll look into it.", ephemeral=True)



    
    @app_commands.command(name="add-embed", description="Send an embed with a custom color")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.describe(hex_color="Hex color code, e.g. #F27DA7")
    @commands.is_owner()
    async def Addembed(self,interaction: discord.Interaction,title:str,description:str, hex_color: str):
        channel=interaction.channel
        # Ensure hex starts with #
        if not hex_color.startswith("#"):
            hex_color = "#" + hex_color

        try:
            # Convert hex to integer for Discord Colour
            color_int = int(hex_color[1:], 16)
        except ValueError:
            await interaction.response.send_message("Invalid hex color code!", ephemeral=True)
            return
        descriptionText = description.replace("\\n", "\n")

        embed = discord.Embed(
            title=title,
            description=descriptionText,
            color=discord.Colour(color_int)
        )

        await channel.send(embed=embed)
        await interaction.response.send_message("Embed sent successfully!", ephemeral=True)


    
    @app_commands.command(name="poll")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.choices(multiple=[ # param name
        app_commands.Choice(name="True", value=1),
        app_commands.Choice(name="False", value=0)

    ])
    async def poll(self,interaction: discord.Interaction,question:str,hour:int, multiple: app_commands.Choice[int],answers:str,atch:discord.Attachment=None):

        print(hour)
        answs=answers.split(",")
        duration = timedelta(hours=hour)
        poll = discord.Poll(

            question=question,  # required
            duration=duration,  # required
            # kwargs
            multiple=multiple.value,  # optional, defaults to False
            layout_type=discord.PollLayoutType.default,  # optional, defaults to discord.PollLayoutType.default
        )
        


        for ans in answs:
            poll.add_answer(
                text=ans
            )

        
        await interaction.channel.send(poll=poll)
        
        if atch!=None:
            file = await atch.to_file()
            await interaction.channel.send(file=file)


async def setup(client:commands.Bot):
    await client.add_cog(MessageUtility(client))