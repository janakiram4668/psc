from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Ram#4668@localhost/enroll'  # Replace dbname with your actual database name
app.config['SECRET_KEY'] = 'your_secret_key'  # Set a secret key for the session management
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Set the login view

# Define User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(10), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Define Course model
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    cost = db.Column(db.Float, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    teacher = db.relationship('User', backref=db.backref('courses', lazy=True))

# Routes
@app.route('/')
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def process_registration():
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']

    new_user = User(username=username, password=password, role=role)
    db.session.add(new_user)
    try:
        db.session.commit()
        return redirect(url_for('login'))
    except Exception as e:
        # Print the error message for debugging
        print("Error:", str(e))
        return "An error occurred while processing your registration: " + str(e)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.password == password:  # Check if the passwords match
            login_user(user)  # Log in the user
            if user.role == 'student':
                return redirect(url_for('student_dashboard'))
            elif user.role == 'teacher':
                return redirect(url_for('teacher_dashboard'))

        return render_template('login.html', error="Invalid username or password")

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()  # Log out the user
    return redirect(url_for('login'))

@app.route('/student/dashboard')
@login_required
def student_dashboard():
    return "Welcome to the student dashboard!"

@app.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    courses = Course.query.all()
    return render_template('teacher_dashboard.html', courses=courses)

@app.route('/create_course', methods=['GET', 'POST'])
@login_required
def create_course():
    if request.method == 'POST':
        course_name = request.form['course_name']
        duration = request.form['duration']
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        cost = float(request.form['cost'])
        
        new_course = Course(course_name=course_name, duration=duration, start_date=start_date, cost=cost, teacher_id=current_user.id)
        db.session.add(new_course)
        db.session.commit()
        return redirect(url_for('teacher_dashboard'))
    return render_template('create_course.html')

@app.route('/my_courses', methods=['GET'])
@login_required
def my_courses():
    courses = Course.query.filter_by(teacher_id=current_user.id).all()
    return render_template('my_courses.html', courses=courses)

if __name__ == '__main__':
    app.run(debug=True)
