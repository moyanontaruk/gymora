#HTTPException = hoe to send error 
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.equipment import Equipment
from app.schemas.equipment import EquipmentCreate, EquipmentRead, EquipmentUpdate



#each entity's endpoint gets their own router file instead of maxload the main.py
#prefix= xxx means every path in this file will end with that so you dont have to repeat each time
#tags = makes it pretty to keep things group together
router = APIRouter(prefix="/equipment", tags=["equipment"])

#post=create a path / so POST /equipment/
#response_model = w/e this function returns, shape it using EquipmentRead schema before sending back
    #where the Read scheme does it's job by guaranteeing the response has the correct shape
    #correct shape is equi.id, name, descript.
#201 is the standard success code to send. default would be 200
@router.post("/", response_model=EquipmentRead, status_code=status.HTTP_201_CREATED)

#payload tells FastAPI the income request must match the equip schema shape. 
    #client sends over JSON but FastAPI will reject if not correct shape before function even runs
def create_equipment(payload: EquipmentCreate, db: Session = Depends(get_db)):
    
    #creating new instance of model(db object)
    #filling in the fields from EquipmentCreate with the validated payload shape.
    equipment = Equipment(
        name=payload.name,
        description=payload.description,
    )
    #stage into session/i intend to save
    db.add(equipment)
    #write it into PostgreSQL, db assigns it's ID
    db.commit()
    #refresh so object knows it's ID
    db.refresh(equipment)
    return equipment

#get = read
#response_model = endpoint returning many items
@router.get("/", response_model=list[EquipmentRead])
def list_equipment(db: Session = Depends(get_db)):

    #select(xx) = building query/ select from xx table
    #does not execute yet, thats the next line
    statement = select(Equipment)

    #runs, scalars() = give me actual Equip. obj. not raw results rows
    #.all()=collect into list
    results = db.execute(statement).scalars().all()
    return results

#{} =path parameter/changeable part of address so GET /equipment/3 or GET /equipment/7
@router.get("/{equipment_id}", response_model=EquipmentRead)
def get_equipment(equipment_id: int, db: Session = Depends(get_db)):
    
    #get 1 row by it's PK, return the matching Equip.
    #db.get() then None... basically every entity will follow the same pattern
        #it's like saying fetch it when it's the same and vail if the item does not exist
    equipment = db.get(Equipment, equipment_id)
    if equipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )
    return equipment

#put = means to update
@router.put("/{equipment_id}",response_model=EquipmentRead)
def update_equipment(equipment_id: int, payload: EquipmentUpdate, db:Session = Depends(get_db)):
    equipment = db.get(Equipment, equipment_id)
    if equipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail= "Equipment not found",
        )
    
    #model_dump = turns the incoming schema into plain dict.
    #exlude_unset=True -> only include fields the client actually sends
        #so they might only send description and no name so only keep that
        #without it, unset fields will update to blank/show None
    updates = payload.model_dump(exclude_unset=True)

    #loop over each field that the client sent and apply to obj. 
    for field, value in updates.items():
        setattr(equipment, field, value)

    db.commit()
    db.refresh(equipment)
    return equipment


#no response_model becaue nothing comes back, it'll just say 204 meaning success code
@router.delete("/{equipment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_equipment(equipment_id: int, db: Session = Depends(get_db)):
    equipment = db.get(Equipment, equipment_id)
    if equipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    #mark this row for removal
    db.delete(equipment)
    db.commit()
    return None