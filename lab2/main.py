from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import database as db
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI(
    title="ІС «Замовлення їжі»",
    description="API для керування замовленнями та меню ресторану (PostgreSQL + Psycopg)",
    version="1.1.0"
)

templates = Jinja2Templates(directory="templates")

# --- Налаштування для Psycopg (PostgreSQL) ---
DB_PARAMS = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "admin",
    "host": "localhost",
    "port": "5432"
}

# Залежність для SQLAlchemy (ORM)
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

# --- МАРШРУТИ АДМІНІСТРАТОРА (CRUD) ---

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
    try:
        user_exists = dbs.query(db.User).filter(db.User.id == user_id).first()
        if not user_exists:
            test_user = db.User(id=user_id, username=f"user_{user_id}", role="user")
            dbs.add(test_user)
            dbs.commit()

        new_order = db.Order(user_id=user_id, dish_id=dish_id, status="В кошику")
        dbs.add(new_order)
        dbs.commit()

        return RedirectResponse(url="/", status_code=303)

    except Exception as e:
        dbs.rollback()
        print(f"Критична помилка замовлення: {e}")
        return HTMLResponse(
            content=f"<h2>Помилка замовлення</h2><p>{str(e)}</p><a href='/'>Назад</a>",
            status_code=500
        )

@app.get("/admin/stats", response_class=HTMLResponse)
def get_stats(request: Request):
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Використовуємо COALESCE, щоб замість NULL отримати 0
                query = """
                    SELECT d.name, 
                           COUNT(o.id) as total_orders, 
                           COALESCE(SUM(d.price), 0) as revenue
                    FROM dishes d
                    LEFT JOIN orders o ON d.id = o.dish_id
                    GROUP BY d.name
                    ORDER BY revenue DESC;
                """
                cur.execute(query)
                stats = cur.fetchall()

        return templates.TemplateResponse("admin_stats.html", {"request": request, "stats": stats})

    except Exception as e:
        return f"Помилка при завантаженні статистики: {str(e)}"