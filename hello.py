from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Integer, String, ForeignKey, Table, Column
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///worship-team-rota/app.db"

db.init_app(app)

class User(db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str]

# class Roster(db.Model):
#     __tablename__ = "roster"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     user_id: Mapped
#     role: Mapped[str]

class Roster(db.Model):
    __tablename__ = "roster"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"))
    role: Mapped[str]

class Service(db.Model):
    __tablename__ = "services"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    date: Mapped[datetime] =  mapped_column(default=lambda: datetime.now(timezone.utc))

with app.app_context():
    db.create_all()

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"