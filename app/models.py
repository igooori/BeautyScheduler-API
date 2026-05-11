from sqlalchemy import String,BigInteger,Column,Integer,DateTime, Compiled
from app.database import Base
from datetime import datetime

class Booking(Base):
    __tablename__ = 'bookings'
    id = Column(Integer,primary_key=True, autoincrement=True)
    client_name = Column(String, nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True))