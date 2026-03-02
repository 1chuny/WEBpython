from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


# Налаштування підключення до PostgreSQL
DATABASE_URL = "postgresql://postgres:admin@localhost:5432/postgres"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    role = Column(String)  # 'admin' або 'user'

class Dish(Base):
    __tablename__ = "dishes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Float)
    description = Column(String)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    dish_id = Column(Integer, ForeignKey("dishes.id"))
    status = Column(String, default="Pending")

Base.metadata.create_all(bind=engine)