from main import app
from httpx import AsyncClient, ASGITransport
import pytest
@pytest.mark.anyio
async def test_welcom():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport,base_url="http://test") as ac:
        response = await ac.get('/')
    assert response.status_code == 200
    assert "Добро пожаловать" in response.json()['message']
@pytest.mark.anyio
async def test_past_time_error():
    payload = {
        "client_name": "прошлое",
        "start_time": "2020-01-01T12:00:00"
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport,base_url="http://test") as ac:
        response = await ac.post('/bookings',json=payload)
    assert response.status_code == 400
    error_message = response.json()['detail']
    assert 'нельзя записаться на прошлое время' in error_message
@pytest.mark.anyio
async def test_time_multiple_error():
    payload = {
        "client_name": "имя клиента",
        "start_time": "2026-05-14T17:01:00"
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport,base_url="http://test") as ac:
        response = await ac.post('/bookings',json=payload)
    assert response.status_code == 400
    error_message = response.json()['detail']
    assert 'нужно только кратное время 10:00, 11:00 и т.д.' in error_message
@pytest.mark.anyio
async def test_master_works_error():
    payload = {
        "client_name": "имя клиента",
        "start_time": "2026-05-11T19:00"
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport,base_url="http://test") as ac:
        response = await ac.post('/bookings',json=payload)
    assert response.status_code == 400
    error_message = response.json()['detail']
    assert 'матсер работает с 10 до 18' in error_message
@pytest.mark.anyio
async def test_add():
    payload = {
        "client_name": "Иван",
        "start_time": "2026-05-11T17:00:00"
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport,base_url="http://test") as ac:
        response = await ac.post("/bookings", json=payload)
    print(f"\nSTATUS: {response.status_code}")
    print(f"BODY: '{response.text}'")
    assert response.status_code == 200
    data = response.json()
    assert data is not None, "СЕРВЕР ВЕРНУЛ ПУСТОТУ!"
    assert data["start_time"] == "2026-05-11T17:00:00"
    assert data["end_time"] == "2026-05-11T18:00:00"
    assert "id" in data
    assert data["client_name"] == "Иван"
@pytest.mark.anyio
async def test_busy():
    payload = {
        "client_name": "Борис",
        "start_time": "2026-05-11T15:00:00"
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport,base_url="http://test") as ac:
        response = await ac.post('/bookings',json=payload)
    assert response.status_code == 200
    async with AsyncClient(transport=transport,base_url="http://test") as ac:
        response2 = await ac.post('/bookings',json=payload)
    assert response2.status_code == 400
    assert "Это время уже занято" in response2.json()['detail']
@pytest.mark.anyio
async def test_delete_status():
    payload = {
        "client_name": "Боря",
        "start_time": "2026-05-12T14:00:00"
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport,base_url="http://test") as ac:
        response = await ac.post("/bookings", json=payload)
    booking_id = response.json()['id']
    async with AsyncClient(transport=transport,base_url="http://test") as ac:
        response = await ac.delete(f'/bookings/{booking_id}')
    assert response.status_code == 200
    assert response.json()['status'] == 'success'
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport,base_url="http://test") as ac:
        response_retry = await ac.delete(f'/bookings/{booking_id}')
    assert response_retry.status_code == 404




