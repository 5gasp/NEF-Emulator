from typing import List, Optional

from pydantic import BaseModel, confloat


# Shared properties | used for request body in endpoint/items.py
#We can declare a UserBase model that serves as a base for our other models. And then we can make subclasses of that model that inherit its attributes
class Point(BaseModel):
    latitude: confloat(ge=-90, le=90)
    longitude: confloat(ge=-180, le=180)

class PathBase(BaseModel):
    description: Optional[str] = None
    points: Optional[List[Point]] = None 
    start_point: Optional[Point] = None
    end_point: Optional[Point] = None
    color: Optional[str] = None

# Properties to receive on item creation
class PathCreate(PathBase):
    pass


# Properties to receive on item update
class PathUpdate(PathBase):
    pass


# Properties shared by models stored in DB
class PathInDBBase(PathBase):
    id: int
    owner_id: int

    class Config: #this class is used to provide configurations to Pydantic
        orm_mode = True #instead of getting a value from a dict (Pydantic Model) {id = data["id"]} you can get it from an attribure (ORM Model) {id = data.id} 


# Properties to return to client
class Path(PathInDBBase):
    pass


# Properties properties stored in DB
class PathInDB(PathInDBBase):
    pass
