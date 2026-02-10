from pydantic import BaseModel, Field,field_validator,model_validator 
from bson import ObjectId
from typing import List,Dict
import pydantic
from discord.ext import commands

class ShowChannelConnections(BaseModel):
    id: ObjectId = Field(default=None, alias="_id")
    guildId:int
    showChannelId:int
    notifyRoleId:int
    activeMessageId:Dict[str,int]= Field(default={})


    @classmethod
    def from_mongo(cls, data: dict):
        obj = cls.model_construct(**data)
        return obj






    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True