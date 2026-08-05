from pydantic import BaseModel, ConfigDict


class EquipmentBase(BaseModel):
    #shorter because it's describing a piece of JSON
    name: str
    #can be str or none, and then default is =None if descript. is empty
    description: str | None = None


#even tho inherting from EquipmentBase, creating a new class to make it known we CREATE now
#this is what client would send
class EquipmentCreate(EquipmentBase):
    pass


#what api returns
class EquipmentRead(EquipmentBase):
    equipment_id: int

#need this line for pydantic to go into Equipment object, pull out whatevr & turns into clean JSON
#w/o this line, it was throw an error
    model_config = ConfigDict(from_attributes=True)


#not inherting from Base b/c that would make name required and we want it optional
class EquipmentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None