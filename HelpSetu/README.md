# HelpSetu Backend System Documentation

This reporting system is a Flask-based web application designed to allow users to report various issues and incidents. This document provides an overview of the system's functionality and how to use it.

## Getting Started

**Installation**: Ensure you have Python installed on your system. Then activate your virtual environment

```
python -m venv venv
```

Then You can install the required dependencies using `pip`:

```
pip install -r requirements.txt
```

**Setting Up the Database**: The Database automatically sets up when you run `app.py`

**Running the Application**: Start the Flask application by running the following command in your terminal:

`python app.py`

**Accessing the Application**: Once the application is running, you can access it by opening a web browser and navigating to `http://localhost:5000`.

## Functionality

### Reporting Issues

Users can report issues by sending a POST request to the `/API/issues` endpoint from a form. They need to provide details such as their name, victim's name, contact information, address, state, district, block, location, and the type of issue. The issue is stored in the database upon successful reporting, and an email notification is sent.
See `functions.py` for input field names.

### User Registration

New users can register by sending a POST request to the `/register` endpoint with their email and password. If the email is not already registered, a new user account is created.

### User Login

Registered users can log in by sending a POST request to the `/login` endpoint with their email and password. If the credentials are valid, the user is logged in.

### Leadership Board

The `/leadership` endpoint provides a list of users along with their IDs, names, and points. This allows users to view the leadership board and see the points earned by each user.

## Endpoints

- **POST `/api/issues`**: Report an issue.
- **POST `/register`**: Register a new user.
- **POST `/login`**: Log in as an existing user.
- **GET `/leadership`**: View the leadership board.

## Dependencies

See `requirements.txt`

## Google Authentication

Click on: https://developers.google.com/gmail/api/quickstart/python to get started

**Step 1**: Click on `A Google cloud project` and follow instructions

![Google cloud Project link](/readme/cloud_project.jpg)

**Step 2**: Click on `Go to OAuth consent screen` and follow instructions

![Google cloud Project link](/readme/consent_screen.jpg)

**Step 3**: Click on `Enable API` and follow instructions

![Google cloud Project link](/readme/enable_api.jpg)

**Step 4**: Click on `Go to Credentials`, follow the instructions, download `credentials.json` and save in root directory.

![Google cloud Project link](/readme/credentials.jpg)

## Running the Application

To run the application, execute the `app.py` file using Python. Make sure to set up the database before running the application.
