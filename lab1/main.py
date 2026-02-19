from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import database as db

app = FastAPI(
    title="ІС «Замовлення їжі»",
    description="API для керування замовленнями та меню ресторану",
    version="1.0.0"
)

templates = Jinja2Templates(directory="templates")

# Залежність для отримання сесії БД
def get_db():
    database = db.SessionLocal()
    try:
        yield database
    finally:
        database.close()

# --- МАРШРУТИ КОРИСТУВАЧА ---

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, dbs: Session = Depends(get_db)):
    dishes = dbs.query(db.Dish).all()
    return templates.TemplateResponse("index.html", {"request": request, "dishes": dishes})

# --- МАРШРУТИ АДМІНІСТРАТОРА (CRUD для Dish) ---

@app.get("/admin", response_class=HTMLResponse)
def admin_panel(request: Request, dbs: Session = Depends(get_db)):
    dishes = dbs.query(db.Dish).all()
    return templates.TemplateResponse("admin.html", {"request": request, "dishes": dishes})

@app.post("/admin/dish/create")
def create_dish(name: str = Form(...), price: float = Form(...), dbs: Session = Depends(get_db)):
    new_dish = db.Dish(name=name, price=price)
    dbs.add(new_dish)
    dbs.commit()
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/dish/update/{dish_id}")
def update_dish(dish_id: int, name: str = Form(...), price: float = Form(...), dbs: Session = Depends(get_db)):
    dish = dbs.query(db.Dish).filter(db.Dish.id == dish_id).first()
    dish.name = name
    dish.price = price
    dbs.commit()
    return RedirectResponse(url="/admin", status_code=303)

@app.get("/admin/dish/delete/{dish_id}")
def delete_dish(dish_id: int, dbs: Session = Depends(get_db)):
    dish = dbs.query(db.Dish).filter(db.Dish.id == dish_id).first()
    dbs.delete(dish)
    dbs.commit()
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/add_to_cart")
def add_to_cart(
        dish_id: int = Form(...),
        user_id: int = Form(...),
        dbs: Session = Depends(get_db)
):
    # Створюємо новий запис у таблиці Order
    new_order = db.Order(user_id=user_id, dish_id=dish_id, status="В кошику")

    dbs.add(new_order)
    dbs.commit()

    # Після додавання повертаємо користувача на головну сторінку
    return RedirectResponse(url="/", status_code=303)