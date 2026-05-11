from fastapi import FastAPI, HTTPException, Depends
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Booking
from app.database import get_db
from fastapi import Path

"""Метод,Аналог в жизни,Зачем нужен в коде?
@app.get(),Посмотреть,"Получить данные (список свободных слотов, инфо о записи)."
@app.post(),Создать,"Отправить данные (создать новую запись, зарегистрировать юзера)."
@app.put(),Заменить,"Полностью обновить запись (например, поменять и имя, и время)."
@app.patch(),Исправить,"Частичное обновление (например, только перенести время, не меняя имя)."
@app.delete(),Удалить,"Отменить запись, удалить пользователя."""

app = FastAPI()

class BookingCreate(BaseModel):
    client_name: str
    start_time: datetime


@app.get('/')
async def welcom():
    return {"message": "Добро пожаловать в систему записи BeautyScheduler!"}
@app.post('/bookings') #эта сама страница /bookings
async def add_db(booking: BookingCreate, db: AsyncSession = Depends(get_db)):
 #делаем чтобы фасапи понял что за букинг
    now = datetime.now(timezone.utc) # длеаем снимок моего пк
    if booking.start_time <= now: # эта проверка если время пользователя меньше или равно тому времени которое у меня на пк то выдаем ему ошибка
        raise HTTPException(status_code=400,detail="нельзя записаться на прошлое время") # здесь ловим ошибка 400 и делаем ее красивой чтобы пользователь понял
    if booking.start_time.minute != 0 or booking.start_time.second != 0: # это проверка если минуты будут не равны 0 или часы будут не равны 0 тогда код падает с ошибкой
        raise HTTPException(status_code=400, detail='нужно только кратное время 10:00, 11:00 и т.д.') # ну и мы эту ошибку делаем красивой и понятной пользователю
    if booking.start_time.hour < 10 or booking.start_time.hour > 17: # если время меньше 10 или больше 17 тогда пишем пользователю что мастер занял
        raise HTTPException(status_code=400, detail='матсер работает с 10 до 18')
    query = select(Booking).where(Booking.start_time == booking.start_time) # мы тут указываем саму таблицу и сравниваем если в таблице лежит одинаковая запись тогда  возвращаем результат если нету записис возвращаем none
    result = await db.execute(query) # это мы вытаскиваем данные из query
    exicuting = result.scalar_one_or_none() # тут мы смотрим сами данные
    if exicuting: # если есть результат говорим что занято
        raise HTTPException(status_code=400, detail='Это время уже занято')
    calculeted_end_time = booking.start_time+timedelta(hours=1) # если незанято тогда добавляет в end_time время и записываем его на 1ч как по тз Расчитывается автоматически: `start_time + 1 час`

    new_booking = Booking(
        client_name=booking.client_name,
        start_time = booking.start_time,
        end_time=calculeted_end_time
    ) # тут мы говорим какие данные в бд уходят а именно время пользователя и его имя и конец
    db.add(new_booking) # тут уже добавляем данные в бд
    await db.commit() # сохраняем
    await db.refresh(new_booking) # делаем рефреш базы данных чтобы увидели новую инфу
    return new_booking
@app.delete('/bookings/{booking_id}') # адресс по котрому можно удалить id
async def delete_bokings(booking_id: int, db: AsyncSession = Depends(get_db)): # обособляем переменные и бд
    query = select(Booking).where(Booking.id == booking_id) # тут ищем id пользователя только непонятно откуда мы его знаем ID чтобы сравнивать
    result = await db.execute(query) # тут мы смотрим пришел ответ от бд или нет
    booking = result.scalar_one_or_none()
    if not booking: # если нет id тогда выводим пользователю
        raise HTTPException(status_code=404, detail='Запись с таким ID ненайдена')
    now = datetime.now(timezone.utc) # смотрим текущее время
    time_dif = booking.start_time - now # тут мы его время отнимаем с временем в реал
    if time_dif < timedelta(hours=2): # тут если меньше 2ч пишем пользователя
        raise HTTPException(status_code=403, detail='Отмена невозможна: до записи осталось меньше 2 часов')
    await db.delete(booking) # добавляем
    await db.commit() # сохраняем
    return{"status": "success", "message": f"Запись {booking_id} успешно удалена"} # возвращаем только непонимаю что за штучки внутри есть



    
    

