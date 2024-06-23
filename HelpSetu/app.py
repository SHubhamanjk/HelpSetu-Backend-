```python
# Import necessary libraries and modules from Flask and other packages
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_login import current_user, UserMixin, LoginManager
from geopy.geocoders import Nominatim
import random
import string

# Initialize the Flask application
app = Flask(__name__)

# Configuration settings for the Flask application
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Database URI for SQLAlchemy
app.config['MAIL_SERVER'] = 'smtp.example.com'  # Mail server settings for Flask-Mail
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@example.com'
app.config['MAIL_PASSWORD'] = 'your_email_password'
app.config['SECRET_KEY'] = 'your_secret_key'  # Secret key for session management and security

# Initialize the extensions with the Flask app
db = SQLAlchemy(app)  # Database instance
mail = Mail(app)  # Mail instance
login_manager = LoginManager(app)  # Login manager instance

# Define the User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)  # User ID
    email = db.Column(db.String(150), unique=True, nullable=False)  # User email, unique and non-nullable
    password = db.Column(db.String(150), nullable=False)  # User password, non-nullable
    point = db.Column(db.Integer, default=0)  # User points, default is 0

# Define the Report model
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Report ID
    name = db.Column(db.String(150), nullable=False)  # Name of the person reporting
    victim_name = db.Column(db.String(150), nullable=False)  # Victim's name
    contact = db.Column(db.String(15), nullable=False)  # Contact information
    address = db.Column(db.String(300), nullable=False)  # Address details
    state = db.Column(db.String(150), nullable=False)  # State
    district = db.Column(db.String(150), nullable=False)  # District
    block = db.Column(db.String(150), nullable=False)  # Block
    location = db.Column(db.String(300), nullable=False)  # Location coordinates
    issue_type = db.Column(db.String(150), nullable=False)  # Type of issue

# Load user by ID for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Function to send an email
def send_email(to_email, subject, message_body):
    msg = Message(subject, sender=app.config['MAIL_USERNAME'], recipients=[to_email])
    msg.body = message_body
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Failed to send email. Error: {e}")
        return False

# Function to get user location using geopy
def get_user_location():
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.geocode("your address here")
    return f"{location.latitude}, {location.longitude}"

# Route to report an issue
@app.route('/api/issues', methods=['POST'])
def report_issue():
    data = request.form
    name = data.get('name')
    victim_name = data.get('victim_name')
    contact = data.get('contact')
    address = data.get('address')
    state = data.get('state')
    district = data.get('district')
    block = data.get('block')
    issue_type = data.get('issue_type')
    location = get_user_location()  # Get the user's location

    # Create a new issue dictionary
    issue = {
        'name': name,
        'victim_name': victim_name,
        'contact': contact,
        'address': address,
        'state': state,
        'district': district,
        'block': block,
        'location': location,
        'issue_type': issue_type
    }

    # Create a new Report object and add it to the database
    new_issue = Report(name=name, victim_name=victim_name, contact=contact, address=address, state=state, district=district, block=block, location=location, issue_type=issue_type)
    db.session.add(new_issue)

    # Update user points if the user is authenticated
    user = current_user
    if user.is_authenticated:
        user.point += 1

    db.session.commit()  # Commit the changes to the database

    # Send an email notification about the new issue
    to_email = 'ngo_email@example.com'
    subject = 'New Issue Reported'
    message_body = f"A new issue has been reported:\n\n{issue}"
    email_sent = send_email(to_email, subject, message_body)

    # Return appropriate response based on email sending status
    if email_sent:
        return jsonify({'message': 'Issue created and email sent successfully'}), 201
    else:
        return jsonify({'message': 'Issue created but failed to send email'}), 201

# Route to register a new user
@app.route('/register', methods=['GET', 'POST'])
def register():
    email = request.form.get('email')
    password = request.form.get('password')
    
    # Check if user with the same email already exists
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'User with Email already Exists'}), 400
    
    # Create a new user and add to the database
    new_user = User(email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully'}), 201

# Route for user login
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()

    # Validate the user's credentials
    if not user or user.password != password:
        return jsonify({'error': 'Invalid email or password'}), 401
    else:
        return jsonify({'message': 'Login successful'}), 200

# Route to get the leadership board
@app.route('/leadership')
def leadership():
    all_users = User.query.all()
    data = []
    for user in all_users:
        user_data = {
            'id': user.id,
            'name': user.name,
            'points': user.point
        }
        data.append(user_data)
    
    return jsonify(data)

# Function to generate a one-time password (OTP)
def generate_otp(length=6):
    otp = ''.join(random.choices(string.digits, k=length))
    return otp

# Function to send an OTP email
def send_otp_email(to_email, otp):
    subject = "Your OTP Code"
    message_body = f"Your OTP code is {otp}"
    send_email(to_email, subject, message_body)

# Route to handle OTP requests
@app.route('/otp', methods=['POST'])
def otp():
    email = request.form.get('email')
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({'error': 'Email not found'}), 404

    otp = generate_otp()
    # Here you should save the OTP to the database or session associated with the user

    send_otp_email(email, otp)
    return jsonify({'message': 'OTP sent successfully'}), 200

# Function to generate a temporary password
def generate_temp_password(length=8):
    temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    return temp_password

# Function to send a temporary password email
def send_temp_password_email(to_email, temp_password):
    subject = "Your Temporary Password"
    message_body = f"Your temporary password is {temp_password}"
    send_email(to_email, subject, message_body)

# Route to handle forgotten passwords
@app.route('/forget_password', methods=['POST'])
def forget_password():
    email = request.form.get('email')
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({'error': 'Email not found in the database'}), 404
    
    temp_password = generate_temp_password()
    user.password = temp_password
    db.session.commit()

    send_temp_password_email(email, temp_password)
    return jsonify({'message': 'Temporary password generated and sent to email successfully'}), 200

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)


### Detailed Explanation

# 1. **Imports**:
#    - Import necessary modules from Flask, SQLAlchemy, Flask-Mail, Flask-Login, and other libraries.

# 2. **App Initialization**:
#    - Create a Flask application instance.
#    - Configure the application with database URI, mail server settings, and secret key.

# 3. **Extensions Initialization**:
#    - Initialize `SQLAlchemy`, `Mail`, and `LoginManager` with the Flask app.

# 4. **Models**:
#    - Define `User` and `Report` models with the required fields and properties.
#    - Use `UserMixin` to integrate Flask-Login functionalities.

# 5. **User Loader**:
#    - Define a function to load user by ID for Flask-Login.

# 6. **Helper Functions**:
#    - `send_email`: Sends an email using Flask-Mail.
#    - `get_user_location`: Uses `geopy` to get the user's location based on an address.



# 7. **Routes**:
#    - `/api/issues`: Handles issue reporting, adds the issue to the database, updates user points if authenticated, and sends an email notification.
#    - `/register`: Handles user registration, checks for existing users, and adds new users to the database.
#    - `/login`: Authenticates users based on email and password.
#    - `/leadership`: Returns a list of all users and their points for a leaderboard.
#    - `/otp`: Generates and sends an OTP to the user's email.
#    - `/forget_password`: Generates a temporary password, updates the user's password, and sends it via email.

# 8. **Main Block**:
#    - Runs the Flask application in debug mode.

# This code snippet provides a comprehensive application with user authentication, issue reporting, email notifications, and other functionalities built using Flask and its extensions.
