from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_login import current_user, UserMixin, LoginManager
from geopy.geocoders import Nominatim
import random
import string

app = Flask(__name__)

# Flask app configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@example.com'
app.config['MAIL_PASSWORD'] = 'your_email_password'
app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)
mail = Mail(app)
login_manager = LoginManager(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    point = db.Column(db.Integer, default=0)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    victim_name = db.Column(db.String(150), nullable=False)
    contact = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(300), nullable=False)
    state = db.Column(db.String(150), nullable=False)
    district = db.Column(db.String(150), nullable=False)
    block = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(300), nullable=False)
    issue_type = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def send_email(to_email, subject, message_body):
    msg = Message(subject, sender=app.config['MAIL_USERNAME'], recipients=[to_email])
    msg.body = message_body
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Failed to send email. Error: {e}")
        return False

def get_user_location():
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.geocode("your address here")
    return f"{location.latitude}, {location.longitude}"

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
    location = get_user_location()

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

    new_issue = Report(name=name, victim_name=victim_name, contact=contact, address=address, state=state, district=district, block=block, location=location, issue_type=issue_type)
    
    db.session.add(new_issue)

    user = current_user
    if user.is_authenticated:
        user.point += 1
    
    db.session.commit()
    
    to_email = 'ngo_email@example.com'
    subject = 'New Issue Reported'
    message_body = f"A new issue has been reported:\n\n{issue}"
    email_sent = send_email(to_email, subject, message_body)

    if email_sent:
        return jsonify({'message': 'Issue created and email sent successfully'}), 201
    else:
        return jsonify({'message': 'Issue created but failed to send email'}), 201

@app.route('/register', methods=['GET', 'POST'])
def register():
    email = request.form.get('email')
    password = request.form.get('password')
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'User with Email already Exists'}), 400
    
    new_user = User(email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()

    if not user or user.password != password:
        return jsonify({'error': 'Invalid email or password'}), 401
    else:
        return jsonify({'message': 'Login successful'}), 200

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

def generate_otp(length=6):
    otp = ''.join(random.choices(string.digits, k=length))
    return otp

def send_otp_email(to_email, otp):
    subject = "Your OTP Code"
    message_body = f"Your OTP code is {otp}"
    send_email(to_email, subject, message_body)

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

def generate_temp_password(length=8):
    temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    return temp_password

def send_temp_password_email(to_email, temp_password):
    subject = "Your Temporary Password"
    message_body = f"Your temporary password is {temp_password}"
    send_email(to_email, subject, message_body)

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

if __name__ == '__main__':
    app.run(debug=True)
