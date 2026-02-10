import discord
from discord import app_commands
from discord.ext import commands

import cv2
import numpy as np
import pytesseract
from ui.UIstats import ScoreStatView


class ScoreStats(commands.Cog):
    def __init__(self, client: discord.Client):
        self.client:commands.Bot = client
        
        #self.client.tree.add_command(self.score_stats)
    score_stats = app_commands.Group(name="score-stats", description="Provides Stats for a specific score end screen screenshot")


    def parese_raw_text(self,Scores,scoreMain,songNameText):
        #lines = [line.strip() for line in text.splitlines() if line.strip()]
        pointScores=Scores.split()

        try:
            text2 = songNameText.split("\n")
            songName=text2[0]
        except:
            songName=songNameText
        
        result = {
            "song": None,
            "score": None,
            "perfect": None,
            "great": None,
            "good": None,
            "bad": None,
            "miss": None
        }

        #if lines:
        #   result["song"] = lines[0]  # Title guess
        i=0
        for word in pointScores:
            if "perfect" == word.lower():
                try:
                    result["perfect"] = int(pointScores[i+1] )
                except:
                    pass

            if "great" == word.lower():
        
                try:
                    result["great"] = int(pointScores[i+1] )
                except:
                    pass

            if "good" == word.lower():
                try:
                    result["good"] = int(pointScores[i+1] )
                except:
                    pass

            if "bad" == word.lower():
                try:
                    result["bad"] = int(pointScores[i+1] )
                except:
                    pass

            if "miss" == word.lower():
                try:
                    result["miss"] = int(pointScores[i+1] )
                except:
                    pass

            i=i+1

        result["song"] = songName
        result["score"] = scoreMain
        return result

    # Helper: Calculate accuracy
    def calculate_accuracy(self,data):
        try:
            perfect = int(data.get("perfect", 0))
            great = int(data.get("great", 0))
            good = int(data.get("good", 0))
            bad = int(data.get("bad", 0))
            miss = int(data.get("miss", 0))
        except ValueError:
            return None

        total = perfect + great + good + bad + miss
        if total == 0:
            return None
        
        negative = great + good * 2 + bad * 3 + miss * 4
        accuracy = ((total * 4 - negative) / (total * 4)) * 100
        return round(accuracy, 3)


    @score_stats.command(name="auto", description="Auto Calculates the score stats from the screenshot")
    @app_commands.describe(file_attachment="Full Screenshot of End Screen of the Score without any distortions or changes")
    async def auto(self,interaction: discord.Interaction,file_attachment:discord.Attachment):
    
        await interaction.response.defer(thinking=True,ephemeral=False)
        interaction_channel=interaction.channel
        avatar_url = interaction.user.display_avatar.url
        # Decode image
        data = await file_attachment.read()
        image_np = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)

        cropped = self.templateCheck(image_np,"template.png")
        cv2.imwrite("cropped.png", cropped)

        config = "--psm 6"
        textScores = pytesseract.image_to_string(cropped, config=config,lang="eng+jpn")
    
        mask=self.ColorFilter(image_np,[160, 115, 230],[200, 160, 255])
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'
        scoreMain = pytesseract.image_to_string(mask, config=custom_config)
    
    
        textName=self.NameCalculator(image_np)
        print(textScores)
        print(scoreMain)
        score_data=self.parese_raw_text(textScores,scoreMain,textName)
        print(score_data)
        accuracy = self.calculate_accuracy(score_data)
    
        file = await file_attachment.to_file()
        #url=f"attachment://{file.filename}"  might need to
    
        score_data["accuracy"]=accuracy if accuracy is not None else "N/A"

        view=ScoreStatView(user=interaction.user,scoreData=score_data,file=file)
        if interaction!=None:
            await interaction.followup.send(ephemeral=False,view=view,file=file)
        else:
            await interaction_channel.send(view=view,file=file)



    @score_stats.command(name="manual", description="useful if auto detection fails, Screenshot still required")
    @app_commands.describe(perfect="Number of Perfects",score="Total Score", great="Number of Greats", good="Number of Goods", bad="Number of Bads", miss="Number of Misses")
    async def manual_score_stats(self,interaction: discord.Interaction,file_attachment:discord.Attachment,score:int, perfect: int, great: int, good: int, bad: int, miss: int,name:str="Not Provided"):
        await interaction.response.defer(thinking=True, ephemeral=False)
        interaction_channel = interaction.channel
        avatar_url = interaction.user.display_avatar.url

        score_data = {
            "perfect": perfect,
            "great": great,
            "good": good,
            "bad": bad,
            "miss": miss,
            "song": name,
            "score": score
        }

        score_data["accuracy"] = self.calculate_accuracy(score_data)

        embed = discord.Embed(title="🎵 Rhythm Game Score(Manually Entered)", color=0x00ffcc)
        file = await file_attachment.to_file()
        #embed.set_image(url=f"attachment://{file.filename}")
    
        view=ScoreStatView(user=interaction.user,scoreData=score_data,file=file)

        embed.set_footer(text="This command might have bugs. If you face any issues, please report them using the command: /report-bug")
        await interaction.followup.send(ephemeral=False,view=view,file=file)



    def templateCheck(self,image_np,template_name):
        template = cv2.imread(template_name)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        image_gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)

        # Create ORB detector
        orb = cv2.ORB_create(3500)  # Higher number = more keypoints

        # Detect keypoints and descriptors
        kp1, des1 = orb.detectAndCompute(template_gray, None)
        kp2, des2 = orb.detectAndCompute(image_gray, None)

        # Match descriptors using Brute Force Matcher
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1, des2)

        # Sort matches by distance (smaller distance = better match)
        matches = sorted(matches, key=lambda x: x.distance)

        # Use only the top matches for homography (avoid outliers)
        good_matches = matches[:50]  # You can tune this number

        # Extract matched keypoints
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        # Compute homography to find template location in screenshot
        H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

        # Get template dimensions
        h, w = template.shape[:2]
        pts = np.float32([[0, 0], [0, h], [w, h], [w, 0]]).reshape(-1, 1, 2)

        # Project template corners into screenshot space
        dst = cv2.perspectiveTransform(pts, H)

        # Draw polygon around detected area
    
    

        # Crop the detected area using bounding rect of transformed points
        x, y, w, h = cv2.boundingRect(np.int32(dst))
        cropped = image_np[y:y+h, x:x+w]
        return cropped


    def ColorFilter(self,image_np,LowerColorList,UpperColorList):
        hsv = cv2.cvtColor(image_np, cv2.COLOR_BGR2HSV)
        height, width = image_np.shape[:2]#gray 103, 69, 69
        # Pink color range (tweak if needed)  169, 122, 242
        lower_color = np.array(LowerColorList)
        upper_color = np.array(UpperColorList)

        mask = cv2.inRange(hsv, lower_color, upper_color)


        # Invert so text becomes black on white
        mask_inv = cv2.bitwise_not(mask)
        kernel = np.ones((2, 2), np.uint8)
        mask_inv = cv2.dilate(mask_inv, kernel, iterations=1)

    # Optional: remove tiny specks
        mask_inv = cv2.medianBlur(mask_inv, 3)#Use this for main score



        return mask_inv


    def NameCalculator(self,image_np):
        height, width = image_np.shape[:2]
        aspect_ratio = (width / height)
        if aspect_ratio<1.6:
            y1Name, y2Name = int(  0.0121951219512195* height), int(0.0567073170731707 * height)  # vertical range
            x1Name, x2Name = int(0.1932203389830508* width), int(0.3983050847457627  * width)  # horizontal range

            
        elif aspect_ratio>1.6 and aspect_ratio<=2.17:
            y1Name, y2Name = int(0.0256410256410256 * height), int(0.0743589743589744 * height)  # vertical range
            x1Name, x2Name = int(0.2464454976303318 * width), int(0.4253554502369668 * width)  # horizontal range
        else:
            y1Name, y2Name = int(0.0305555555555556* height), int(0.0703703703703704 * height)  # vertical range
            x1Name, x2Name = int(0.2569105691056911* width), int(0.4422764227642276 * width)  # horizontal range"""

            y1Scores,y2Scores = int(0.561* height), int(0.89907 * height)  # vertical range
            x1Scores, x2Scores = int(0.289* width), int(0.357* width)  # horizontal range



        cropped = image_np[y1Name:y2Name, x1Name:x2Name]
        # OCR with pytesseract
        config = "--psm 6"
        text = pytesseract.image_to_string(cropped, config=config,lang="eng+jpn")
        try:
            res=text.split("\n")
            return res[0]
        except:
            return text








async def setup(client:commands.Bot):
    await client.add_cog(ScoreStats(client))