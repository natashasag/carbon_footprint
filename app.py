from flask import Flask, render_template, redirect, url_for, flash, request
from config import Config
from models import db, User, Entry, LoginHistory
from forms import RegisterForm, LoginForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import json
from calc import compute_co2
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
login = LoginManager(app)
login.login_view = 'login'
@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter((User.username==form.username.data)|(User.email==form.email.data)).first():
            flash('That username or email is already taken. Try something else.', 'warning')
            return render_template('register.html', form=form)
        hashed = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed)
        db.session.add(user); db.session.commit()
        flash('Account created — welcome!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)
@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        user = User.query.filter_by(username=username).first()
        ip = request.remote_addr or 'unknown'
        success = False
        user_id = None
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            success = True
            user_id = user.id
            flash('Signed in. Ready to calculate?', 'success')
        else:
            flash('Invalid credentials — try again.', 'danger')
        lh = LoginHistory(user_id=user_id, username_attempt=username, ip_address=ip, success=success)
        db.session.add(lh); db.session.commit()
        if success:
            return redirect(url_for('questionnaire'))
    return render_template('login.html', form=form)
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Signed out — come back soon!', 'info')
    return redirect(url_for('index'))
@app.route('/questionnaire', methods=['GET','POST'])
@login_required
def questionnaire():
    if request.method == 'POST':
        payload = {
            'daily_car_km': float(request.form.get('daily_car_km',0)),
            'daily_bus_km': float(request.form.get('daily_bus_km',0)),
            'daily_train_km': float(request.form.get('daily_train_km',0)),
            'weekly_flight_hours': float(request.form.get('weekly_flight_hours',0)),
            'monthly_electricity_kwh': float(request.form.get('monthly_electricity_kwh',0)),
            'meals_per_day': int(request.form.get('meals_per_day',3)),
            'meat_meal_ratio': float(request.form.get('meat_meal_ratio',0.5)),
            'trees_planted': int(request.form.get('trees_planted',0))
        }
        result = compute_co2(payload)
        entry = Entry(user_id=current_user.id, data=json.dumps(payload), co2_kg=result['total_kg_co2_per_year'], category=result['category'])
        db.session.add(entry); db.session.commit()
        return render_template('results.html', result=result, breakdown=result['breakdown'])
    return render_template('questionnaire.html')
@app.route('/dashboard')
@login_required
def dashboard():
    entries = Entry.query.filter_by(user_id=current_user.id).order_by(Entry.date.desc()).limit(20).all()
    recent_logins = LoginHistory.query.filter_by(user_id=current_user.id).order_by(LoginHistory.timestamp.desc()).limit(10).all()
    return render_template('dashboard.html', entries=entries, recent_logins=recent_logins)
if __name__ == '__main__':
    app.run(debug=True)
