import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime

# --- App and Database Configuration ---
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'habits.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Database Models ---
class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    logs = db.relationship('Log', backref='habit', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Habit {self.name}>'

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    log_date = db.Column(db.Date, nullable=False)
    habit_id = db.Column(db.Integer, db.ForeignKey('habit.id'), nullable=False)

    def __repr__(self):
        return f'<Log {self.log_date}>'

# --- Application Routes ---
@app.route('/')
def index():
    habits = Habit.query.order_by(Habit.created_at.desc()).all()
    today = date.today()
    habits_with_status = []
    for habit in habits:
        log_today = Log.query.filter_by(habit_id=habit.id, log_date=today).first()
        habits_with_status.append((habit, log_today is not None))
    return render_template('index.html', habits_with_status=habits_with_status)

@app.route('/add', methods=['POST'])
def add_habit():
    habit_name = request.form.get('habit_name')
    if habit_name:
        new_habit = Habit(name=habit_name)
        db.session.add(new_habit)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/log/<int:habit_id>', methods=['POST'])
def log_habit(habit_id):
    today = date.today()
    # Prevent duplicate logs for the same day
    existing_log = Log.query.filter_by(habit_id=habit_id, log_date=today).first()
    if not existing_log:
        log = Log(habit_id=habit_id, log_date=today)
        db.session.add(log)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:habit_id>', methods=['POST'])
def delete_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    db.session.delete(habit)
    db.session.commit()
    return redirect(url_for('index'))

# --- Main Execution ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Creates the database tables if they don't exist
    app.run(debug=True, port=5001)

# Powered by Innovate CLI, a product of vaidik.co
