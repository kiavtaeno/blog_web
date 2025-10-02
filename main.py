from storage import save_data, load_data
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime
import threading
import uvicorn
import os
import json
import webbrowser
import time

from starlette.responses import RedirectResponse

app = FastAPI(title="апи самого крутого блога")

templates = Jinja2Templates(directory="templates")
current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(current_dir, "templates")

class Traveler(BaseModel):
    email: str
    username: str
    password: str

class TravelerUpdate(BaseModel):
    email: str = None
    username: str = None
    password: str = None

class Journey(BaseModel):
    travelerId: int
    destination: str
    story: str

class JourneyUpdate(BaseModel):
    destination: str = None
    story: str = None


travelers, journeys, next_traveler_id, next_journey_id = load_data()

if not travelers:
    travelers.append({
        "id": 1,
        "email": "wanderer@travel.com",
        "username": "Челик",
        "password": "wander123",
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    })
    next_traveler_id = 2

if not journeys:
    journeys.append({
        "id": 1,
        "travelerId": 1,
        "destination": "Горы Алтая",
        "story": "Мои первые впечатления от путешествия по Алтайским горам...",
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    })
    next_journey_id = 2
    save_data(travelers, journeys, next_traveler_id, next_journey_id)

@app.get("/")
async def home_page(request: Request):
    journeys_with_authors = []
    for journey in journeys:
        traveler = next((t for t in travelers if t["id"] == journey["travelerId"]), None)
        journeys_with_authors.append({
            "journey": journey,
            "traveler": traveler
        })
    return templates.TemplateResponse("index.html", {
        "request": request,
        "journeys": journeys_with_authors
    })

@app.get("/api-info", response_class=HTMLResponse)
async def api_info_page(request: Request):
    return templates.TemplateResponse("api_info.html", {
        "request": request,
        "travelers": travelers,
        "journeys": journeys
    })

@app.get("/users", response_class=HTMLResponse)
async def users_page(request: Request):
    return templates.TemplateResponse("users.html", {
        "request": request,
        "travelers": travelers
    })

@app.get("/journeys/{journey_id}")
async def view_journey(request: Request, journey_id: int):
    journey = next((j for j in journeys if j["id"] == journey_id), None)
    if not journey:
        return HTMLResponse(
            "<h1>404 - Пост не найден</h1><p>Такой публикации не существует</p><a href='/'>На главную</a>",
            status_code=404
        )
    traveler = next((t for t in travelers if t["id"] == journey["travelerId"]), None)
    return templates.TemplateResponse("post.html", {
        "request": request,
        "journey": journey,
        "traveler": traveler
    })

@app.get("/create-journey")
async def create_journey_page(request: Request):
    return templates.TemplateResponse("create_post.html", {
        "request": request,
        "travelers": travelers
    })

@app.get("/edit-journey/{journey_id}")
async def edit_journey_page(request: Request, journey_id: int):
    journey = next((j for j in journeys if j["id"] == journey_id), None)
    if not journey:
        return HTMLResponse(
            "<h1>404 - Пост не найдено</h1><p>Нельзя редактировать несуществующую публикацию</p><a href='/'>На главную</a>",
            status_code=404
        )
    return templates.TemplateResponse("edit_post.html", {
        "request": request,
        "journey": journey,
        "travelers": travelers
    })

@app.post("/create-journey")
async def create_journey_form(
        request: Request,
        travelerId: int = Form(...),
        destination: str = Form(...),
        story: str = Form(...)
):
    global next_journey_id

    # Проверяем существование пользователя
    traveler_exists = any(t["id"] == travelerId for t in travelers)
    if not traveler_exists:
        return templates.TemplateResponse("create_post.html", {
            "request": request,
            "travelers": travelers,
            "error": "❌ Пользователь не найден",
            "form_data": {"travelerId": travelerId, "destination": destination, "story": story}
        })

    # Валидация названия
    if len(destination) < 2:
        return templates.TemplateResponse("create_post.html", {
            "request": request,
            "travelers": travelers,
            "error": "❌ Название слишком короткое (минимум 2 символа)",
            "form_data": {"travelerId": travelerId, "destination": destination, "story": story}
        })

    if len(story) < 10:
        return templates.TemplateResponse("create_post.html", {
            "request": request,
            "travelers": travelers,
            "error": "❌ Сообщение слишком короткое (минимум 10 символов)",
            "form_data": {"travelerId": travelerId, "destination": destination, "story": story}
        })

    new_journey = {
        "id": next_journey_id,
        "travelerId": travelerId,
        "destination": destination,
        "story": story,
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    }
    journeys.append(new_journey)
    next_journey_id += 1
    save_data(travelers, journeys, next_traveler_id, next_journey_id)
    return RedirectResponse(url="/", status_code=303)

@app.post("/edit-journey/{journey_id}")
async def edit_journey_form(
        request: Request,
        journey_id: int,
        travelerId: int = Form(...),
        destination: str = Form(...),
        story: str = Form(...)
):
    journey = next((j for j in journeys if j["id"] == journey_id), None)
    if not journey:
        return templates.TemplateResponse("edit_post.html", {
            "request": request,
            "journey": journey,
            "travelers": travelers,
            "error": "❌ Путешествие не найдено"
        })

    traveler_exists = any(t["id"] == travelerId for t in travelers)
    if not traveler_exists:
        return templates.TemplateResponse("edit_post.html", {
            "request": request,
            "journey": journey,
            "travelers": travelers,
            "error": "❌ Пользователь не найден"
        })

    if len(destination) < 2:
        return templates.TemplateResponse("edit_post.html", {
            "request": request,
            "journey": journey,
            "travelers": travelers,
            "error": "❌ Название слишком короткое (минимум 2 символа)"
        })

    if len(story) < 10:
        return templates.TemplateResponse("edit_post.html", {
            "request": request,
            "journey": journey,
            "travelers": travelers,
            "error": "❌ Сообщение слишком короткое (минимум 10 символов)"
        })

    journey["travelerId"] = travelerId
    journey["destination"] = destination
    journey["story"] = story
    journey["updatedAt"] = datetime.now()
    save_data(travelers, journeys, next_traveler_id, next_journey_id)
    return RedirectResponse(url=f"/journeys/{journey_id}", status_code=303)

@app.post("/delete-journey/{journey_id}")
async def delete_journey(journey_id: int):
    global journeys
    journeys = [j for j in journeys if j["id"] != journey_id]
    save_data(travelers, journeys, next_traveler_id, next_journey_id)
    return RedirectResponse(url="/", status_code=303)

@app.post("/api/travelers/")
async def create_traveler(traveler: Traveler):
    global next_traveler_id

    for t in travelers:
        if t["email"] == traveler.email:
            raise HTTPException(status_code=400, detail="Email уже используется")

    if len(traveler.password) < 6:
        raise HTTPException(status_code=400, detail="Пароль должен быть не менее 6 символов")

    new_traveler = {
        "id": next_traveler_id,
        "email": traveler.email,
        "username": traveler.username,
        "password": traveler.password,
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    }
    travelers.append(new_traveler)
    next_traveler_id += 1
    save_data(travelers, journeys, next_traveler_id, next_journey_id)
    return new_traveler

@app.get("/api/travelers/")
async def get_travelers():
    return travelers

@app.get("/api/travelers/{traveler_id}")
async def get_traveler(traveler_id: int):
    traveler = next((t for t in travelers if t["id"] == traveler_id), None)
    if not traveler:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return traveler

@app.put("/api/travelers/{traveler_id}")
async def update_traveler(traveler_id: int, traveler_update: TravelerUpdate):
    traveler = next((t for t in travelers if t["id"] == traveler_id), None)
    if not traveler:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if traveler_update.email:
        traveler["email"] = traveler_update.email
    if traveler_update.username:
        traveler["username"] = traveler_update.username
    if traveler_update.password:
        traveler["password"] = traveler_update.password

    traveler["updatedAt"] = datetime.now()
    save_data(travelers, journeys, next_traveler_id, next_journey_id)
    return traveler

@app.delete("/api/travelers/{traveler_id}")
async def delete_traveler(traveler_id: int):
    global travelers
    travelers = [t for t in travelers if t["id"] != traveler_id]
    save_data(travelers, journeys, next_traveler_id, next_journey_id)
    return {"message": "Пользователь удален"}

@app.post("/api/journeys/")
async def create_journey(journey: Journey):
    global next_journey_id

    traveler_exists = any(t["id"] == journey.travelerId for t in travelers)
    if not traveler_exists:
        raise HTTPException(status_code=400, detail="Пользователь не найден")

    new_journey = {
        "id": next_journey_id,
        "travelerId": journey.travelerId,
        "destination": journey.destination,
        "story": journey.story,
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    }
    journeys.append(new_journey)
    next_journey_id += 1
    save_data(travelers, journeys, next_traveler_id, next_journey_id)
    return new_journey

@app.get("/api/journeys/")
async def get_journeys():
    return journeys

@app.get("/api/journeys/{journey_id}")
async def get_journey(journey_id: int):
    journey = next((j for j in journeys if j["id"] == journey_id), None)
    if not journey:
        raise HTTPException(status_code=404, detail="Пост не найден")
    return journey

@app.put("/api/journeys/{journey_id}")
async def update_journey(journey_id: int, journey_update: JourneyUpdate):
    journey = next((j for j in journeys if j["id"] == journey_id), None)
    if not journey:
        raise HTTPException(status_code=404, detail="Пост не найден")

    if journey_update.destination:
        journey["destination"] = journey_update.destination
    if journey_update.story:
        journey["story"] = journey_update.story

    journey["updatedAt"] = datetime.now()
    save_data(travelers, journeys, next_traveler_id, next_journey_id)
    return journey

@app.delete("/api/journeys/{journey_id}")
async def delete_journey_api(journey_id: int):
    global journeys
    journeys = [j for j in journeys if j["id"] != journey_id]
    save_data(travelers, journeys, next_traveler_id, next_journey_id)
    return {"message": "Пост удален"}

def open_browser():
    time.sleep(2)
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    print("🚀 Запуск блога о путешествиях...")
    print("📝 Доступные страницы:")
    print("   Главная страница: http://127.0.0.1:8000")
    print("   API информация: http://127.0.0.1:8000/api-info")
    print("\n🔧 API endpoints (для разработчиков):")
    print("   API путешественников: http://127.0.0.1:8000/api/travelers/")
    print("   API путешествий: http://127.0.0.1:8000/api/journeys/")

    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=8000)