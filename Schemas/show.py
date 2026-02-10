# schemas
from pydantic import BaseModel, Field,field_validator,model_validator 
from bson import ObjectId
from typing import List,Dict
import pydantic
import requests
import datetime
print(pydantic.VERSION)
#model_construct function mongo db while getting back the data
class Show(BaseModel):
    id: ObjectId = Field(default=None, alias="_id")   
    showId:int
    name:str
    banner:str
   # ended:bool=Field(default=False)
    Schedule:List
    state:str=Field(default="UPCOMING") #UPCOMING,ONGOING,ENDED

    @field_validator("banner",mode="after")
    def normalize_banner(cls, value):
        try:
            r=requests.get(url=value)
            return value
        except:

            return "https://storage.sekai.best/sekai-en-assets/virtual_live/select/banner/"+f"{value}/{value}.png"

    @field_validator("Schedule",mode="after")
    def convert_schedule(cls, value):
        l=len(value)
        for i in range(0,l):
            if i==0 or i==l-1 or i==(l//2):
                value[i].ping=True
            value[i] = value[i].model_dump(by_alias=True, exclude_none=True)  
        return value

    @classmethod
    def from_mongo(cls, data: dict):
        """Constructs a UserSchema from MongoDB data without running unwanted conversions."""
        obj = cls.model_construct(**data)  # ⚠️ model_construct skips all validation  
        l=len(obj.Schedule)
        for i in range(0,l):
            obj.Schedule[i] = ShowSchedule(**obj.Schedule[i])   
        return obj

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

class ShowSchedule(BaseModel):
    start: int
    end: int
    seq: int
    ping: bool = Field(default=False)
    complete: bool = Field(default=False)


    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
