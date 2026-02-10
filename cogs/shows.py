import discord
from discord import app_commands
from discord.ext import commands
import requests
import json
from pymongo.asynchronous.database import AsyncDatabase
from datetime import datetime,timezone,timedelta
from discord.ext import tasks
from Schemas.show import ShowSchedule,Show
from Schemas.settingSchema import ShowChannelConnections
import asyncio
import time
from ui.UIshow import ShowDisplay,CounterButton
import aiohttp
import io
from typing import Dict


class Shows(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.db:AsyncDatabase=client.mongodb
        self.show_collection=self.db["shows"]
        self.showChannel_collection=self.db["showChannelConnections"]
        
        #self.show_time_check.start()
        self.localScheduleDict:Dict={}
        self.localShowViews:Dict={}
        
    # Slash command

    #@app_commands.command(name="testload", description="Adds a show notification channel")
    #@app_commands.default_permissions(manage_messages=True)
    async def register_views(self):
       
        channelSetting=  self.showChannel_collection.find()
        channelSettings=await channelSetting.to_list(length=10)
        
        print("guh")
        

        for setting in channelSettings:
                try:
                    print("viewcheck2")
                    setting_obj=ShowChannelConnections.from_mongo(setting)
                    for show_id,message_id in setting_obj.activeMessageId.items():
                        print("viewcheck3")
                        ch=setting_obj.showChannelId
                        ch=await self.client.fetch_channel(ch)
                        msg=await ch.fetch_message(message_id)
                        print(id)
                        cont=msg.components[0].children
                        print(cont)
                        if str(show_id) in self.localShowViews:
                            view = self.localShowViews[str(show_id)]
                        else:
                            view = ShowDisplay(
                                scheduleText=cont[4].content,
                                url=cont[1].items[0].media.url,
                                localScheduleList=self.localScheduleDict[str(show_id)])
                        self.client.add_view(view=view,message_id=message_id)
                        print("viewcheck4")
                        """view=ShowDisplay.from_message(msg,timeout=None)
                        
                        client.add_view(view=view,message_id=id)
                        print("viewcheck5")"""
                    
                except:
                    pass
    async def cog_load(self):
         await self.check_new_show()
         await self.show_time_check()
         await self.register_views()

         await asyncio.sleep(10)
         self.check_new_show.start()
         self.show_time_check.start()
        #return await super().cog_load()



    





    async def url_to_file(url:str,filename:str):
         try:
            async with aiohttp.ClientSession() as s:
                async with s.get(url=url) as r:
                    return discord.File(io.BytesIO(await r.read()), filename=filename)

         except:
            return None

    @app_commands.command(name="testui", description="For ui testing")
    @app_commands.default_permissions(manage_messages=True)
    async def testui(self, interaction: discord.Interaction):
        channel=interaction.channel
        view=ShowDisplay(scheduleText="hi",url="https://storage.sekai.best/sekai-en-assets/virtual_live/select/banner/vlentrance_00330/vlentrance_00330.png")
        async with aiohttp.ClientSession() as s:
            async with s.get("https://storage.sekai.best/sekai-en-assets/virtual_live/select/banner/vlentrance_00330/vlentrance_00330.png") as r:
                file=discord.File(io.BytesIO(await r.read()), filename="SEKAI.png")

        msg=await channel.send(view=view,file=file)
       


    

    async def testLoad(self,view:ShowDisplay,startTimeSecondStamp,schdText,bar_length,total_time,
                       oldmessageObj:discord.Message,loading,formatted_totalTime,
                       show:Show,schedule:ShowSchedule,cont,sep,
                       showFile:discord.File,
                       setting_obj:ShowChannelConnections):
    
        
        #view=discord.ui.LayoutView.from_message(oldmessageObj,timeout=None)
        #cont=oldmessageObj.components[0].children
            
        #view=ShowDisplay(scheduleText=cont[3].content,url=cont[1].items[0].media.url,localScheduleList=self.localScheduleDict[str(show.showId)])
        
        newMsg=await oldmessageObj.channel.send(view=view,file=showFile)
        try:
            await newMsg.pin()
        except:
            pass
        try:
            await oldmessageObj.delete()
        except:
            pass
        #await messageObj.edit(view=view)
        
        setting_obj.activeMessageId[str(show.showId)]=newMsg.id
        new_setting_dict=setting_obj.model_dump(by_alias=True, exclude_none=True)
        await self.showChannel_collection.update_one({"_id":setting_obj.id},{"$set":new_setting_dict})

        if schedule.ping:
            pingmsg=await newMsg.reply(f"<@&{setting_obj.notifyRoleId}> Starting in <t:{int(schedule.start/1000)}:R>")
        else:
            pingmsg=await newMsg.reply(f"Starting in <t:{int(schedule.start/1000)}:R>")


        now=datetime.now().timestamp()
        asyncio.create_task(    self.checkAfterShowEnd(sleeptime=((schedule.end//1000)-(now)),
                                                                               cont=cont,
                                                                               loading=loading,
                                                                               sep=sep,
                                                                               show=show,
                                                                               setting_obj=setting_obj,newMsg=newMsg,schedule=schedule,schdText=schdText,view=view)    ) 


        await asyncio.sleep(startTimeSecondStamp - now )  # Sleep until 1 minute before start time

        if show.Schedule[-1].seq==schedule.seq:
            schdText.content=f"`Last:` Show {schedule.seq} Ongoing!"
        else:
            schdText.content=f"Show {schedule.seq} Ongoing!"
        loop = asyncio.get_event_loop()
        start_time = loop.time()
        

        interval=5
        while True:
            elapsed = loop.time() - start_time
            progress = min(elapsed / total_time, 1.0)  # clamp between 0–1
            filled = int(bar_length * progress)
            bar = "<:IMG_0263:1428641882766049352>" * filled + "<:loadingblank:1428642199507304569>" * (bar_length - filled)
            #percent = int(progress * 100)
            minutes = int(elapsed // 60)      # integer division
            seconds = int(elapsed % 60)       # remainder
            formatted_time = f"{minutes:02d}:{seconds:02d} "

            loading.content=f"{formatted_time} {bar} {formatted_totalTime}"
            await newMsg.edit(view=view)
            if progress >= 1.0:
                break

            #target_next = start_time + (int(elapsed) + 1)
            target_next = start_time + ((int(elapsed) // interval) + 1) * interval
            delay = max(0, target_next - loop.time())
            await asyncio.sleep(delay)
        await asyncio.sleep(2)

        

        """if pingmsg:
            await pingmsg.delete()"""
        


    async def checkAfterShowEnd(self,sleeptime,cont,loading,sep,show:Show,schedule:ShowSchedule,schdText,view:ShowDisplay,setting_obj,newMsg):
        await asyncio.sleep(sleeptime+7)
        cont.remove_item(loading)
        cont.remove_item(sep)
        if show.state!="ENDED":
            next_schedule:ShowSchedule=show.Schedule[schedule.seq]
            if show.Schedule[-1].seq==schedule.seq:
                schdText.content=f"`Last:` Show {next_schedule.seq} will start in <t:{int(next_schedule.start/1000)}:R>"
            else:
                 
                schdText.content=f"Show {next_schedule.seq} will start in <t:{int(next_schedule.start/1000)}:R>"     
        else:
            butt:CounterButton=view.find_item(100)
            butt.disabled=True
            del(setting_obj.activeMessageId[str(show.showId)])
            new_setting_dict=setting_obj.model_dump(by_alias=True, exclude_none=True)
            await self.showChannel_collection.update_one({"_id":setting_obj.id},{"$set":new_setting_dict})
            schdText.content="# Show Ended!"
        
        await newMsg.edit(view=view)








    #async def endShowMsg(self,msg:discord.Message,view:ShowDisplay):
         
    def scheduleStore(self,show:Show):
        key = str(show.showId)
        if key not in self.localScheduleDict:
            self.localScheduleDict[key] = show.Schedule

    

   







    @tasks.loop(seconds=60)
    async def show_time_check(self):
        print("checking shows")
        
        now= datetime.now().timestamp()*1000
        #shows= self.show_collection.find({"Schedule": {"$elemMatch": {"start": {"$gt": now}}},"state":{"$ne":"ENDED"}})
        shows= self.show_collection.find({"state":{"$ne":"ENDED"}})
        async for show in shows:
            show_dict={}
            show_obj=Show.from_mongo(show)
            self.scheduleStore(show_obj)
            for index, schedule in enumerate(show_obj.Schedule):
                
                if not schedule.complete and schedule.end>now:   
                    if schedule.start>now:
                        channelSettings=  self.showChannel_collection.find()
                        channelSettings=await channelSettings.to_list(length=100)

                        days=3  # if show.Schedule[-1].seq==schedule.seq:

                        #viewcheck
                        if str(show_obj.showId) not in self.localShowViews:
                            if show_obj.Schedule[-1].seq==schedule.seq:
                                view=ShowDisplay(scheduleText=f"`Last:` Show {schedule.seq} will start in <t:{int(schedule.start/1000)}:R>",url=show_obj.banner,localScheduleList=self.localScheduleDict[str(show_obj.showId)])     
                                self.localShowViews[str(show_obj.showId)]=view
                            else:
                                view=ShowDisplay(scheduleText=f"Show {schedule.seq} will start in <t:{int(schedule.start/1000)}:R>",url=show_obj.banner,localScheduleList=self.localScheduleDict[str(show_obj.showId)])
                                self.localShowViews[str(show_obj.showId)]=view
                        else:
                            view=self.localShowViews[str(show_obj.showId)]



                        if schedule.start-now<(60000*60*24*days) and   schedule.start-now>(60000*3)   :
                                #showFile=await self.url_to_file(show_obj.banner)    
                                
                                for setting in channelSettings:
                                    setting_obj=ShowChannelConnections.from_mongo(setting)
                                    channel=await self.client.fetch_channel(setting_obj.showChannelId)                                    
                              
                                    try:
                                            msg=await channel.fetch_message(setting_obj.activeMessageId[str(show_obj.showId)])
                                    except:
                                            
                                            msg=await channel.send(view=view)
                                            try:
                                                await msg.pin()
                                            except:
                                                pass
                                            setting_obj.activeMessageId[str(show_obj.showId)]=msg.id
                                            new_setting_dict=setting_obj.model_dump(by_alias=True, exclude_none=True)
                                            await self.showChannel_collection.update_one({"_id":setting_obj.id},{"$set":new_setting_dict})

                                    
                                print("loop1")
                                        
                                break

                                if show_obj.state=="UPCOMING":
                                    show_obj.state="ONGOING"
                                schedule.complete=True
                                if schedule.seq==len(show_obj.Schedule):
                                    show_obj.state="ENDED"
                                
                                
                        elif schedule.start-now<=(60000*3):
                            showFile=await self.url_to_file(show_obj.banner)       

                            startTimeSecondStamp=int(schedule.start/1000)
        
                            total_time=(schedule.end-schedule.start)/1000
                            minutes = int(total_time // 60)      # integer division
                            seconds = int(total_time % 60) 
                            formatted_totalTime = f"{minutes:02d}:{seconds:02d}"
                            bar_length = 10
                            #view=self.localShowViews[str(show.showId)]
    
                            loading=discord.ui.TextDisplay(content=f" 00:00 "+("<:loadingblank:1428642199507304569>"*bar_length) + f" {formatted_totalTime}")
                            cont:discord.ui.Container=view.find_item(2000)
                            sep=discord.ui.Separator()
                            cont.add_item(sep)
                            cont.add_item(loading)
                            schdText:discord.ui.TextDisplay=cont.find_item(500)
                            if show_obj.Schedule[-1].seq==schedule.seq:
                                schdText.content=f"`Last:` Show {schedule.seq} will start in <t:{int(schedule.start/1000)}:R>"
                            else:
                                schdText.content=f"Show {schedule.seq} will start in <t:{int(schedule.start/1000)}:R>"


                            for setting in channelSettings:
                                setting_obj=ShowChannelConnections.from_mongo(setting)
                                channel=await self.client.fetch_channel(setting_obj.showChannelId) 
                                                                   
                            
                                try:
                                        msg=await channel.fetch_message(setting_obj.activeMessageId[str(show_obj.showId)])
                                except:
                                        #view=ShowDisplay(scheduleText=f"Show {schedule.seq} will start in <t:{int(schedule.start/1000)}:R>",url=show_obj.banner,localScheduleList=self.localScheduleDict[str(show_obj.showId)])
                                        msg=await channel.send(view=view)
                                        setting_obj.activeMessageId[str(show_obj.showId)]=msg.id
                                        new_setting_dict=setting_obj.model_dump(by_alias=True, exclude_none=True)
                                        await self.showChannel_collection.update_one({"_id":setting_obj.id},{"$set":new_setting_dict})

                                asyncio.create_task(self.testLoad(view=view,startTimeSecondStamp=startTimeSecondStamp,
                                                                  schdText=schdText,
                                                                  bar_length=bar_length,
                                                                  total_time=total_time,
                                                                  oldmessageObj=msg,
                                                                  loading=loading,formatted_totalTime=formatted_totalTime,
                                                                  show=show_obj,
                                                                  schedule=schedule,cont=cont,sep=sep,showFile=showFile,
                                                                  setting_obj=setting_obj))
                                
                            show_obj.Schedule[index].complete=True
                            print("loop2")
                            break
            if show_obj.state=="UPCOMING":
                if show_obj.Schedule[0].start<now:
                    show_obj.state="ONGOING"
            elif show_obj.state=="ONGOING":
                if show_obj.Schedule[-1].complete or now>show_obj.Schedule[-1].start:
                    show_obj.state="ENDED"
                    
                                
            #print(show_obj.state)
            show_dict = show_obj.model_dump(by_alias=True, exclude_none=True)
            await self.show_collection.update_one({"_id":show_obj.id},{"$set":show_dict})
                    
           
    @app_commands.command(name="add_show_channel", description="Adds a show notification channel")
    @app_commands.default_permissions(manage_messages=True)
    async def add_show_channel(self, interaction: discord.Interaction, channel: discord.TextChannel,ping_role:discord.Role):
        channelsetting=ShowChannelConnections(guildId=interaction.guild.id,
                               showChannelId=channel.id,
                               notifyRoleId=ping_role.id
        )
        channelsetting_dict=channelsetting.model_dump(by_alias=True, exclude_none=True)
        await self.showChannel_collection.update_one({
            "guildId": interaction.guild.id
        }, {"$setOnInsert": channelsetting_dict}, upsert=True)

        
        await interaction.response.send_message(f"Added {channel.mention} as a show notification channel and {ping_role.mention if ping_role else 'no role'} to be pinged!",ephemeral=True)
        await interaction.channel.send(content=f"Added {channel.mention} as a show notification channel with role: {ping_role.mention if ping_role else 'no role'}",allowed_mentions=discord.AllowedMentions(roles=False))


    @app_commands.command(name="restart_showcheck", description="Restarts the show check task")
    @commands.is_owner()
    async def restart_showcheck(self, interaction: discord.Interaction):
        self.check_new_show.restart()
        await interaction.response.send_message(f"Show check task restarted by {interaction.user.name}!")




    @app_commands.command(name="add_manual_show", description="Add a manual show")
    @commands.is_owner()
    async def add_manual_show(self, interaction: discord.Interaction,show_id:int,show_name:str,show_banner:str,total_shows:int,first_show_start:int,first_show_end:int,show_hour_diff:int):
        #self.check_new_show.restart(self, interaction: discord.Interaction)
        await interaction.response.defer(ephemeral=True)
        schedule_list=[]
        for s in range(0,total_shows):
            difference=(s *show_hour_diff*3600*1000 )
            timestampStart = first_show_start + difference
            timestampEnd = first_show_end + difference
            
            schedule_list.append(ShowSchedule(
                start=timestampStart,
                end=timestampEnd,
                seq=s+1
            ))

        show_obj=Show(
                showId=show_id,
                name=show_name,
                banner=show_banner,
                Schedule=schedule_list
            )
        show_dict = show_obj.model_dump(by_alias=True, exclude_none=True)
        await self.show_collection.insert_one(show_dict)

        await interaction.followup.send("Show Added")

                                                



    @tasks.loop(hours=24)
    async def check_new_show(self):
        
        res=requests.get("https://raw.githubusercontent.com/Sekai-World/sekai-master-db-en-diff/refs/heads/main/virtualLives.json")
        now= datetime.now().timestamp()*1000
        data=res.json()
        for show in data:
            if show["virtualLiveSchedules"] and len(show["virtualLiveSchedules"])>0:
                
                if show["virtualLiveSchedules"][0]["startAt"]>now or show["virtualLiveSchedules"][0]["startAt"]>now and show["virtualLiveSchedules"][-1]["startAt"]<now or show["virtualLiveSchedules"][-1]["startAt"]>now:
                    print("reached till here")
                    data=await self.show_collection.find_one({"showId":show["id"]})
                    
                    if not data:
                        print("running")
                        schedule_list=[]
                        for schd in show["virtualLiveSchedules"]:
                            schedule_list.append(ShowSchedule(
                                start=schd["startAt"],
                                end=schd["endAt"],
                                seq=schd["seq"])
                            )
                        show_obj=Show(
                            showId=show["id"],
                            name=show["name"],
                            banner=show["assetbundleName"],
                            Schedule=schedule_list
                        )
                        show_dict = show_obj.model_dump(by_alias=True, exclude_none=True)
                        await self.show_collection.insert_one(show_dict)

    
    async def check_show_message_exists(self, show:Show,sch:ShowSchedule):
        now= datetime.now().timestamp()*1000
        channelSettings=  self.showChannel_collection.find()
        channelSettings=await channelSettings.to_list(length=100)
        setting_obj=ShowChannelConnections.from_mongo(setting)
        channel=await self.client.fetch_channel(setting_obj.showChannelId)
        for setting in channelSettings:
                for schedule in sch:
                    if(schedule.start-now>(60000*2) and schedule.start-now<=(60000*60*24*4) ): 
                            try:
                                msg=await channel.fetch_message(setting_obj.activeMessageId[str(show.showId)])
                                break
                            except:
                                msg=await channel.send(f"{show.name} - {schedule.seq} will start in <t:{int(schedule.start/1000)}:R>")
                                setting_obj.activeMessageId[str(show.showId)]=msg.id
                                new_setting_dict=setting_obj.model_dump(by_alias=True, exclude_none=True)
                                await self.showChannel_collection.update_one({"_id":setting_obj.id},{"$set":new_setting_dict})
                                break
                                
                                





        
# Required setup function
async def setup(client):
    await client.add_cog(Shows(client))
