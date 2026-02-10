import discord
import discord.ui 
from discord.ui import Container, LayoutView, TextDisplay,Separator,Button,Section
import aiohttp
from typing import List
from utils.logger import Logger
class CounterButton(Button):
    def __init__(self,localScheduleList:List):
        super().__init__(label="Full Schedule", style=discord.ButtonStyle.primary,custom_id="hihihi",id=100)
        self.localScheduleList=localScheduleList
        try:
            self.buttonview=ScheduleListDisplay(localScheduleList=self.localScheduleList)
        except Exception as e:
            print(f"Error in Button View Creation: {e}")
        
        
    async def callback(self, i: discord.Interaction):
        u=i.user
        await i.response.send_message(view=self.buttonview,ephemeral=True)
        await Logger.send_log(f"**Full Schedule**  clicked by `{u}`")


class ShowContainer(Container):
    def __init__(self,scheduleText,url,localScheduleList:List):
        super().__init__()
        self.id=2000

        virtualShow=TextDisplay("# Virtual Show")
        url = url
        gallery = discord.ui.MediaGallery(
        discord.MediaGalleryItem(url, description = "Alt text")
        )
        #schedule=TextDisplay("## Schedule")
        scheduleText=TextDisplay(scheduleText,id=500)
        section=Section(TextDisplay("## Schedule"),accessory=CounterButton(localScheduleList=localScheduleList))

        self.add_item(virtualShow)
        self.add_item(gallery)
        self.add_item(section)
        self.add_item(Separator(visible=False,spacing=discord.SeparatorSpacing.large))
        self.add_item(scheduleText)
        
        
    
    

class ShowDisplay(LayoutView):
    def __init__(self,scheduleText,url,localScheduleList:List):
        super().__init__(timeout=None)
        #self.timeout=None
        
        
        container=ShowContainer(scheduleText=scheduleText,url=url,localScheduleList=localScheduleList)
        self.add_item(container)


class ScheduleListDisplay(LayoutView):
    def __init__(self,localScheduleList:List):
        super().__init__()
        #self.timeout=None
        
        
        container=ScheduleListDisplayContainer(localScheduleList=localScheduleList)
        self.add_item(container)

class ScheduleListDisplayContainer(Container):
    def __init__(self,localScheduleList:List):
        super().__init__()
        schTitle=TextDisplay("# Show Schedule")
        self.add_item(schTitle)
        self.add_item(Separator())

        for sch in localScheduleList:   
            self.add_item(TextDisplay(content=f"Show {sch.seq}:<t:{sch.start//1000}:f>"))
            
        

        

        
    
        
    