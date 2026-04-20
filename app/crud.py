from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Booking

class BookingName(BaseModel):
    client_name: str
class BookigServices(BaseModel):
    services_name: str
app = FastAPI()

app.post('/bookings/name')
async def name_client(name: BookingName, db: AsyncSession = Depends(get_db)):
    new_user = Booking(client_name=name)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"id": new_user.id, "msg": "имя записано запомни свой ID"}
