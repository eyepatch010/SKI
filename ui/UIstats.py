
import discord
import discord.ui 
from discord.ui import Container, LayoutView, TextDisplay,Separator,Button,Section
import aiohttp
from typing import List



class ScoreStatView(discord.ui.LayoutView):
        def __init__(self, *,user:discord.User,scoreData,file:discord.File):
            super().__init__()
            self.user=user
            self.add_item(profileContainer(user=self.user,scoreData=scoreData,file=file))

class profileContainer(discord.ui.Container):
        def __init__(self, *,user:discord.User,scoreData,file:discord.File):
            super().__init__()
            self.user=user
            section=discord.ui.Section(f"# \n\n{self.user.name}",accessory=discord.ui.Thumbnail(media=self.user.display_avatar.url))
            self.add_item(section)
            self.add_item(discord.ui.Separator())
            self.add_item(discord.ui.MediaGallery(discord.MediaGalleryItem(media=file)))
            self.add_item(discord.ui.Separator())
            self.add_item(discord.ui.TextDisplay("# <:purple_note_gem:1423051479274623056> `Pjsk Song Score Accuracy%`\n"))
            
            self.add_item(discord.ui.TextDisplay(f"**Song:** {scoreData['song'] or 'Unknown'}\n"))
            self.add_item(discord.ui.TextDisplay(f"**Score:** {scoreData['score'] or 'N/A'}\n"))
            self.add_item(discord.ui.Separator())
            self.add_item(discord.ui.TextDisplay(f"<:gem:1423200323815739504> **Perfect:** {scoreData['perfect'] or '0'} <:VS:1423199127159701687>"))
            self.add_item(discord.ui.TextDisplay(f"<:gem:1423200323815739504> **Great:** {scoreData['great'] or '0'}"))
            self.add_item(discord.ui.TextDisplay(f"<:gem:1423200323815739504> **Good:** {scoreData['good'] or '0'}"))
            self.add_item(discord.ui.TextDisplay(f"<:gem:1423200323815739504> **Bad:** {scoreData['bad'] or '0'}"))
            self.add_item(discord.ui.TextDisplay(f"<:gem:1423200323815739504> **Miss:** {scoreData['miss'] or '0'}"))
            self.add_item(discord.ui.Separator())
            if scoreData["accuracy"]==100:
                self.add_item(discord.ui.TextDisplay(f"## <a:emu_sparkle:1423062985441808497> `Accuracy:` {scoreData['accuracy']or 'N/A'}% <:purple_gem:1423051515215478784>\n"))

            elif scoreData["accuracy"]>=99 and scoreData["accuracy"]<100:
                self.add_item(discord.ui.TextDisplay(f"## <:EmuWoa:1423062940147384414> `Accuracy:` {scoreData['accuracy'] or 'N/A'}%\n")) 
            elif scoreData["accuracy"]>=90 and scoreData["accuracy"]<99:
                self.add_item(discord.ui.TextDisplay(f"## <:EmuYay:1423193616796618752> `Accuracy:` {scoreData['accuracy'] or 'N/A'}%\n"))   
            elif scoreData["accuracy"]<90 and scoreData["accuracy"]>=80:
                self.add_item(discord.ui.TextDisplay(f"## <:emu_excited:1423193804936183829> `Accuracy:` {scoreData['accuracy'] or 'N/A'}%\n"))
            elif scoreData["accuracy"]<80 and scoreData["accuracy"]>=50:
                self.add_item(discord.ui.TextDisplay(f"## <:emu_huh:1423062914679705622> `Accuracy:` {scoreData['accuracy'] or 'N/A'}%\n"))
            elif scoreData["accuracy"]<50 and scoreData["accuracy"]>=30:
                self.add_item(discord.ui.TextDisplay(f"## <:EmuChiquita:1423063141151014962> `Accuracy:` {scoreData['accuracy'] or 'N/A'}%\n"))
            elif scoreData["accuracy"]<30 and scoreData["accuracy"]>=10:
                self.add_item(discord.ui.TextDisplay(f"## <a:EmuSprintBack:1423063030165536970> `Accuracy:` {scoreData['accuracy'] or 'N/A'}%\n"))
            elif scoreData["accuracy"]<10 and scoreData["accuracy"]>0:
                self.add_item(discord.ui.TextDisplay(f"## <:emu_ball:1423195253585739796> `Accuracy:` {scoreData['accuracy'] or 'N/A'}%\n"))
            elif scoreData["accuracy"]==0:
                self.add_item(discord.ui.TextDisplay(f"## <a:emuexplode:1423195736669163550> `Accuracy:` {scoreData['accuracy'] or 'N/A'}% <:emucatstare:1423196331727519794>\n"))

                self.add_item(discord.ui.TextDisplay(f"### Congratulations for making it this far<:KanaJudge:1423195573200224256>\n"))

