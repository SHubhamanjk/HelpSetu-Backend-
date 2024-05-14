from flask import Flask, request, jsonify
from flask_login import current_user, login_required
from flask_sqlalchemy import SQLAlchemy
from functions import UserModel, ReportModel, send_email, get_user_location


app = Flask(__name__)

# To configure database, typem name and path
# 'sqlite:///users.db' is to set the database name, replace `users` with what name you prefer
# Database file is stored in /instance
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# see function.py for more details
User = UserModel(db=db)
Report = ReportModel(db, app)


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
    # Get user's location
    location = get_user_location()

    # Create a dictionary for issue
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
    # Adding new entry to the database
    new_issue = Report(name=name, victim_name=victim_name, contact=contact, address=address, state=state, district=district, block=block, location=location, issue_type=issue_type)
    
    db.session.add(new_issue)

    user = current_user
    if user.is_authenticated:
        user.point += 1
    
    send_email('<your_email_here />', issue)

    db.session.commit()
    
    # Return a success response
    return jsonify({'message': 'Issue created successfully'}), 201


@app.route('/register', methods=['GET', 'POST'])
def register():
    email = request.form.get('email')
    password = request.form.get('password')
    
    # Check if the email being registered already exists
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'User with Email already Exists'}), 400  # Return error with status code 400 (Bad Request)
    
    # Create a new user
    new_user = User(email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    
    # Return success response
    return jsonify({'message': 'User registered successfully'}), 201  # Return success message with status code 201 (Created)


# Login
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    # Check if the email exists in the database
    user = User.query.filter_by(email=email).first()

    if not user or user.password != password:
        # Return an error response
        return jsonify({'error': 'Invalid email or password'}), 401  # 401 Unauthorized status code
    else:
        # Return a success response
        return jsonify({'message': 'Login successful'}), 200  # 200 OK status code


@app.route('/leadership')
def leadership():
    # Retrieve data from the database
    all_users = User.query.all()
    # Prepare the data for JSON response
    data = []
    for user in all_users:
        user_data = {
            'id': user.id,
            'name': user.name,
            'points': user.point
        }
        data.append(user_data)
    
    # Return JSON response
    return jsonify(data)
    # returns a json [{'id', 'name', 'points'}]


# This is an alternative to running the file from command line
if __name__ == '__main__':
    app.run(debug=True)
