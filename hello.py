from flask import Flask, render_template, request, abort, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import ForeignKey, select
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"

db.init_app(app)

class User(db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str]

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
    return "<h1>Hello, World!</h1>"

@app.route("/users")
def get_users():
    all_users = select(User)       
    result = db.session.execute(all_users)
    user_list = result.scalars().all()
    return render_template('users.html', users=user_list)

@app.route('/users/<int:user_id>/edit')
def edit_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)
    return render_template("edit_user.html", user=user)

@app.route("/update_user/<int:user_id>", methods=['POST'])
def update_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)
    new_username = request.form.get("username")
    new_email = request.form.get("email")
    user.username = new_username
    user.email = new_email
    db.session.commit()
    return redirect(url_for("get_users"))

@app.route("/delete_user/<int:user_id>", methods=['POST'])
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("get_users"))

@app.route("/services")
def get_services():
    all_services = select(Service)       
    result = db.session.execute(all_services)
    services_list = result.scalars().all()
    return render_template("services.html", services=services_list)

@app.route("/services/<int:service_id>/edit")
def edit_service(service_id):
    service = db. session.get(Service, service_id)
    if service is None:
        abort(404)
    return render_template("edit_service.html", service=service)

@app.route("/update_service/<int:service_id>", methods=['POST'])
def update_service(service_id):
   service = db.session.get(Service, service_id) 
   if service is None:
       abort(404)
   new_name = request.form.get("name")
   new_date = datetime.fromisoformat(request.form.get("date"))
   service.name = new_name
   service.date = new_date
   db.session.commit()
   return redirect(url_for("get_services"))

@app.route("/delete_service/<int:service_id>", methods=['POST'])
def delete_service(service_id):
    service = db.session.get(Service, service_id)
    if service is None:
        abort(404)
    db.session.delete(service)
    db.session.commit()
    return redirect(url_for("get_services"))

@app.route("/service/<int:service_id>/roster")
def get_service_roster(service_id):
    service = db.session.get(Service, service_id)
    if service is None:
        abort(404)
    roster = db.session.execute(select(Roster).where(Roster.service_id == service_id))
    roster_list = roster.scalars().all()
    users_in_roster = []
    for r in roster_list:
        user = db.session.get(User, r.user_id)
        if user not in users_in_roster:
            users_in_roster.append(user)
    return render_template("roster.html", rosters=roster_list, service=service, users=users_in_roster)

@app.route("/signup")
def signup():
    return render_template('signup.html')

@app.route("/create_user", methods=["POST"])
def create_user():
    username = request.form.get("username")
    email = request.form.get("email")

    db.session.add(User(username=username, email=email))
    db.session.commit()

    return redirect(url_for("get_users"))

@app.route("/add_service")
def add_service():
    return render_template('add_service.html')

@app.route("/service/<int:service_id>/add_to_roster", methods=['GET', 'POST'])
def add_to_roster(service_id):
    if request.method == "POST":
        user_id = request.form.get("user")
        role = request.form.get("role")
        db.session.add(Roster(user_id=user_id, service_id=service_id, role=role))
        db.session.commit()
        return redirect(url_for("get_service_roster", service_id=service_id))
    all_users = db.session.execute(select(User))
    user_list = all_users.scalars().all()
    service = db.session.get(Service, service_id)
    if service is None:
        abort(404)
    return render_template("add_to_roster.html", users=user_list, service=service)

@app.route("/service/<int:service_id>/roster/<int:roster_id>/delete", methods=['POST'])
def delete_from_roster(roster_id, service_id):
    service = db.session.get(Service, service_id)
    roster = db.session.get(Roster, roster_id)
    if service is None or roster is None:
        abort(404)
    db.session.delete(roster)
    db.session.commit()
    return redirect(url_for("get_service_roster", service_id=service_id))


@app.route("/create_service", methods=["POST"])
def create_service():
    name = request.form.get("name")
    date = datetime.fromisoformat(request.form.get("date"))

    db.session.add(Service(name=name, date=date))
    db.session.commit()

    return redirect(url_for("get_services"))
