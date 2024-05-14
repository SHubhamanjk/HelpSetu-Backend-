def UserModel(db):
    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(80), unique=True, nullable=False)
        password = db.Column(db.String(80), nullable=False)
        point = db.Column(db.Integer)

    return User
    # Returns user object so that it can be used in adding, loggin and deleting user account


"""
//  Code Explanation
--> def create_profile_db(db)
    # Here i'm importing `db` from app.py --> db = SQLAlchemy(app)
    The function paramter, `db` inherits everything from `db`

"""
def ReportModel(db, app):
    class Report(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100))
        contact = db.Column(db.String(100))
        victim_name = db.Column(db.String(255))
        address = db.Column(db.String(255))
        state = db.Column(db.String(100))
        district = db.Column(db.String(100))
        block = db.Column(db.String(100))
        location = db.Column(db.String(100))
        issue_type = db.Column(db.String(100))

    with app.app_context():
        db.create_all()

    return Report
    # Returns Report object so that it can be used in adding, and deleting record


def send_email(r_email, issue):
    import base64
    from email.mime.text import MIMEText
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from requests import HTTPError
    
    SCOPES = [
            "https://www.googleapis.com/auth/gmail.send"
        ]
    flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
    
    creds = flow.run_local_server(port=0)

    service = build('gmail', 'v1', credentials=creds)
    
    message = MIMEText(f"I am reporting an issue regarding {issue['issue_type']} that occurred at {issue['victim_name']}'s residence located at {issue['address']}, {issue['block']}, {issue['district']}, {issue['state']}. The incident was witnessed by {issue['name']} who can be contacted at {issue['contact']}. Thank you for your attention to this matter.")
    message['to'] = r_email
    message['subject'] = f'{issue['issue_type']} Report'
    create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
    
    try:
        message = (service.users().messages().send(userId="me", body=create_message).execute())
        print(F'sent message to {message} Message Id: {message["id"]}')
    except HTTPError as error:
        print(F'An error occurred: {error}')
        message = None


def get_user_location(request):
    import geocoder
    ip = request.remote_addr

    location = geocoder.ip(ip)

    if location.ok:
        return location.latlng  # Returns a tuple (latitude, longitude)
    else:
        return None
