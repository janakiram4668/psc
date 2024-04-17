from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Ram#4668@localhost/enroll'  # Replace dbname with your actual database name
db = SQLAlchemy(app)

# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(10), nullable=False)

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
            if user.role == 'student':
                return redirect(url_for('student_dashboard'))
            elif user.role == 'teacher':
                return redirect(url_for('teacher_dashboard'))

        return render_template('login.html', error="Invalid username or password")

    return render_template('login.html')

@app.route('/student/dashboard')
def student_dashboard():
    return "Welcome to the student dashboard!"

@app.route('/teacher/dashboard')
def teacher_dashboard():
    return "Welcome to the teacher dashboard!"

if __name__ == '__main__':
    app.run(debug=True)
