from flask import Flask, render_template, request, abort, redirect, url_for, session, flash
from sqlalchemy.engine import url
from config import Config
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import ForeignKey, select
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)

app.secret_key = "1234"
app.config.from_object(Config)

db.init_app(app)



class User(db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str | None]
    access_level: Mapped[str] = mapped_column(default="member")
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


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

def setup_admin():
    email = os.environ.get("ADMIN_EMAIL")
    password = os.environ.get("ADMIN_PASSWORD")
    stmt = db.session.execute(select(User).where(User.access_level=="admin"))
    admin_exists = stmt.scalars().one_or_none()

    if not admin_exists:
        new_admin = User(username="admin", email=email, access_level="admin")
        new_admin.set_password(password)
        db.session.add(new_admin)
        db.session.commit()

with app.app_context():
    db.create_all()
    setup_admin()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "email" not in session:
            flash('Please log in to access this page', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', email=session['email'])

@app.route('/logout')
def logout():
    session.clear()
    flash("You've been logged out!", "info")
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'email' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        # Input validation
        if not email or not password:
            flash("Please fill all the fields.", 'warning')
            return render_template("login.html")

        stmt = db.session.execute(select(User).where(User.email == email))
        user = stmt.scalars().one_or_none()

        if user is None:
            flash('Invalid email or password', 'warning')
            return render_template('login.html')

        if user.check_password(password):
            session.clear()
            session.permanent = True
            session["email"] = email
            flash("Logged in successfully!", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid email or password", 'warning')

    return render_template("login.html")



@app.route("/users")
@login_required
def get_users():
    all_users = select(User)       
    result = db.session.execute(all_users)
    user_list = result.scalars().all()
    return render_template('users.html', users=user_list)

@app.route('/users/<int:user_id>/edit')
@login_required
def edit_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)
    return render_template("edit_user.html", user=user)

@app.route("/update_user/<int:user_id>", methods=['POST'])
@login_required
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
@login_required
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("get_users"))

@app.route("/services")
@login_required
def get_services():
    all_services = select(Service)       
    result = db.session.execute(all_services)
    services_list = result.scalars().all()
    return render_template("services.html", services=services_list)

@app.route("/services/<int:service_id>/edit")
@login_required
def edit_service(service_id):
    service = db. session.get(Service, service_id)
    if service is None:
        abort(404)
    return render_template("edit_service.html", service=service)

@app.route("/update_service/<int:service_id>", methods=['POST'])
@login_required
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
@login_required
def delete_service(service_id):
    service = db.session.get(Service, service_id)
    if service is None:
        abort(404)
    db.session.delete(service)
    db.session.commit()
    return redirect(url_for("get_services"))

@app.route("/service/<int:service_id>/roster")
@login_required
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
@login_required
def create_user():
    user = User()
    user.username = request.form.get("username")
    user.email = request.form.get("email")
    password = request.form.get("password")
    user.set_password(password)
   
    db.session.add(user)
    db.session.commit()

    return redirect(url_for("get_users"))

@app.route("/add_service")
@login_required
def add_service():
    return render_template('add_service.html')

@app.route("/service/<int:service_id>/add_to_roster", methods=['GET', 'POST'])
@login_required
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
@login_required
def delete_from_roster(roster_id, service_id):
    service = db.session.get(Service, service_id)
    roster = db.session.get(Roster, roster_id)
    if service is None or roster is None:
        abort(404)
    db.session.delete(roster)
    db.session.commit()
    return redirect(url_for("get_service_roster", service_id=service_id))


@app.route("/create_service", methods=["POST"])
@login_required
def create_service():
    name = request.form.get("name")
    date = datetime.fromisoformat(request.form.get("date"))

    db.session.add(Service(name=name, date=date))
    db.session.commit()

    return redirect(url_for("get_services"))
