import discord
from discord import app_commands
from discord.ext import commands
import gspread
from google.oauth2.service_account import Credentials
import cv2
import numpy as np
import pytesseract
from ui.UIstats import ScoreStatView
from pymongo.asynchronous.database import AsyncDatabase
from PIL import Image
import time
import io
from sekaiInformer.settings import settings


class SheetManager(commands.Cog):
    def __init__(self, client: discord.Client):
        self.client:commands.Bot = client
        #self.db:AsyncDatabase=client.mongodb
        self.scopes=["https://www.googleapis.com/auth/spreadsheets"]
        self.creds = Credentials.from_service_account_file("sheet_reader_key.json",scopes=self.scopes)
        self.sheet_client = gspread.authorize(self.creds)
        self.sheet_link=settings.SHEET_LINK  
        
        #self.client.tree.add_command(self.score_stats)
    
  

    @app_commands.command(name="next_hour", description="sheet checker command")
    #@app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_any_role(1342952556552519821,1401345103737524250,1291519101558194228,1318373713791549511,1291515230152691774,1274940106968666184)
    #@app_commands.check(owner_check)
    async def sheetmain(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        spreadsheet = self.sheet_client.open_by_url(self.sheet_link)
        sheet = spreadsheet.worksheet("Schedule G1")
        
        
        """
        
        records = sheet.get_all_records(
            head=1,              # row number where headers would normally be
            expected_headers=["ET", "PT", "UTC", "GST","JST","Hour","P1","P2","P4","P5","StandbyFiller","Manager","StandbyManager","Timestamp"]
        )

        await interaction.followup.send(dayData)"""
        headers = sheet.row_values(1)

        col_index = headers.index("Timestamp") + 1




        timestamp = int(time.time())

        col = sheet.col_values(col_index)[2:]

        for i in range(0,len(col)):
            if col[i]=="":
                continue
            
            stamp=int(col[i])
            if stamp-timestamp<60*60 and stamp-timestamp>=0:
                row = sheet.row_values(i+2+1) 
                break
        print(row)
        embed=discord.Embed(
            color=discord.Color.blue(),
            title="Next Hour",
        )
        embed.add_field(name="Time",value=f"<t:{row[18]}:R>",inline=False)
        embed.add_field(name="P1",value=row[7] if row[7] else "```Empty```",inline=True)
        embed.add_field(name="P2",value=row[8] if row[9] else "```Empty```",inline=True)
        embed.add_field(name="P3",value=row[9] if row[9] else "```Empty```",inline=True)
        embed.add_field(name="P4",value=row[10] if row[10] else "```Empty```",inline=True)
        embed.add_field(name="P5",value=row[11] if row[11] else "```Empty```",inline=True)
        embed.add_field(name="Standby Filler",value=row[13] if row[13] else "```Empty```",inline=True)
        embed.add_field(name="Manager",value=row[15] if row[15] else "```Empty```",inline=False)
        embed.add_field(name="Standby Manager",value=row[16] if row[16] else "```Empty```",inline=True)
        embed.add_field(name="Order",value=f"```{row[19]}```" if row[19] else "```Unknown```",inline=False)
        embed.add_field(name="Checkin",value=f"```{row[20]}```" if row[20] else "```Unkown```",inline=False)



        await interaction.followup.send("Response sent",ephemeral=True)
        await interaction.channel.send(embed=embed)


    def sheetvalues(self):
        s = self.sheet_client.open_by_url(self.sheet_link)
        sheet = s.worksheet("Schedule G1")
            
        values = sheet.get_all_values()[1:]   # skip first row

        my_headers = ["ET", "PT", "UTC", "GST","JST","Hour","P1","P2","P4","P5","StandbyFiller","Manager","StandbyManager","Timestamp","Order","Checkin","Messages"]

        columns = {
            header: [row[i] if i < len(row) else "" for row in values]
            for i, header in enumerate(my_headers)
        }
        return columns

        #await interaction.followup.send(dayData)


async def setup(client:commands.Bot):
    await client.add_cog(SheetManager(client))

