import json
import os
import datetime
import uuid
import bcrypt
from pymongo import MongoClient
import streamlit as st
from utils import get_database, hash_password, verify_password

def get_database():
    CONNECTION_STRING = "mongodb+srv://vikaspedia2024:NMh8eGRLcSf8tSMM@streamlitdb.9eediwg.mongodb.net/?retryWrites=true&w=majority&appName=streamlitDB"
    try:
        conn = MongoClient(CONNECTION_STRING)
        print("Connected successfully!!!")
        return conn.AgriBot
    except:
        print("Could not connect to MongoDB")
        return

db = get_database()

users_file_path = os.path.join("user_database", "users.json")

def hash_password(password):
    """Hash a password for storing."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def register_user(username, password, user_uuid):
    """Register a new user with MongoDB and local JSON storage."""
    try:
        if os.path.exists(users_file_path):
            with open(users_file_path, 'r') as file:
                try:
                    users = json.load(file)
                except json.JSONDecodeError:
                    users = {}  # Initialize as empty dict if JSON is corrupt or empty
        else:
            users = {}
    except Exception as e:
        print(f"Failed to handle users file: {e}")
        return False

    user_exists_in_file = username in users
    user_exists_in_db = db.users.find_one({"username": username}) if db is not None else False

    if user_exists_in_file or user_exists_in_db:
        print("User already exists.")
        return False

    hashed_password = hash_password(password)

    if db is not None:
        try:
            db.users.insert_one({
                "username": username,
                "password": hashed_password,
                "uuid": user_uuid
            })
            print("User added to MongoDB successfully with UUID.")
        except Exception as e:
            print(f"Error adding user to MongoDB: {e}")
            return False

    users[username] = {
        "password": hashed_password.decode('utf-8'),
        "uuid": user_uuid
    }

    try:
        with open(users_file_path, 'w') as file:
            json.dump(users, file)
        st.session_state["user_uuid"] = user_uuid  # Set user_uuid in session state
        st.session_state["username"] = username  # Set username in session state
        print("User added to local JSON file successfully.")
        return True
    except Exception as e:
        print(f"Failed to save users to file: {e}")
        return False

def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user."""
    if isinstance(stored_password, str):
        stored_password = stored_password.encode('utf-8')
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)

def login_user(username, password):
    db = get_database()  # Ensure your database connection is correct
    users_file_path = os.path.join("user_database", "users.json")

    # Check MongoDB first
    if db is not None:
        user = db.users.find_one({"username": username})
        if user:
            if verify_password(user['password'], password):
                user_uuid = user.get('uuid')
                if user_uuid:
                    log_activity(username, user_uuid, "login")
                    return True, user_uuid
                else:
                    st.error("Error: UUID not found for the user.")
                    return False, None
            else:
                st.error("Error: Incorrect password.")
                return False, None
        else:
            st.error("Error: Username does not exist.")
            return False, None

    # If MongoDB is not available, check the local JSON file
    if os.path.exists(users_file_path):
        with open(users_file_path, 'r') as file:
            users = json.load(file)
            user_data = users.get(username)
            if user_data:
                if verify_password(user_data['password'], password):
                    user_uuid = user_data.get('uuid')
                    if user_uuid:
                        log_activity(username, user_uuid, "login")
                        return True, user_uuid
                    else:
                        st.error("Error: UUID not found for the user.")
                        return False, None
                else:
                    st.error("Error: Incorrect password.")
                    return False, None
            else:
                st.error("Error: Username does not exist.")
                return False, None

    return False, None  # Ensure this is the default return if all checks fail

def log_activity(username, uuid, action):
    activities_file_path = os.path.join("user_database", "activities.json")
    current_time = datetime.datetime.now().isoformat()
    
    # Load existing activities from the local JSON file
    activities = []
    if os.path.exists(activities_file_path):
        try:
            with open(activities_file_path, 'r') as file:
                activities = json.load(file)
        except json.JSONDecodeError:
            # Handle empty or invalid JSON by initializing activities as an empty list
            activities = []
        except Exception as e:
            print(f"An unexpected error occurred while loading activities: {e}")
    
    # Append the new activity to the local list, including the UUID
    activities.append({"timestamp": current_time, "username": username, "uuid": uuid, "activity_type": action})
    
    # Save the updated activities back to the file
    with open(activities_file_path, 'w') as file:
        json.dump(activities, file, indent=4)  # Adding indent for better readability
    print("Activity logged in local file successfully.")
    
    # Attempt to add the new activity to MongoDB, including the UUID
    if db is not None:
        try:
            db.activity_log.insert_one({"timestamp": current_time, "username": username, "uuid": uuid, "action": action})
            print("Activity logged in MongoDB successfully.")
        except Exception as e:
            print(f"Error logging activity in MongoDB: {e}")

def show_logout_button():
    if "authenticated" in st.session_state and st.session_state["authenticated"]:
        if st.button('Logout'):
            process_logout(st.session_state["username"])

def process_registration(username, password):
    """Process registration and handle errors using Streamlit's session state for UI interaction."""
    if not username.strip() or not password.strip():
        st.error("Username and password cannot be empty. Please choose valid credentials.")
        return

    user_uuid = str(uuid.uuid4())  # Generate a UUID for the new user

    if register_user(username, password, user_uuid):
        # Set session state upon successful registration
        st.session_state["authenticated"] = True
        st.session_state["username"] = username
        st.session_state["uuid"] = user_uuid
        st.success("Registration successful!")
        print("Registration successful, session state:", st.session_state)  # Debug print
        st.rerun()  # Force a rerun of the application to reflect authenticated state
    else:
        st.error("Registration failed. Username might already be in use.")

def process_login(username, password):
    """Process user login and update session state."""
    if not username.strip() or not password.strip():
        st.error("Username and password cannot be empty. Please enter your credentials.")
        return

    authenticated, user_uuid = login_user(username, password)
    if authenticated:
        # Set session state upon successful login
        st.session_state["authenticated"] = True
        st.session_state["username"] = username
        st.session_state["uuid"] = user_uuid
        st.success("Logged in successfully!")
        print("Login successful, session state:", st.session_state)  # Debug print
        st.rerun()  # Refresh the application to reflect the authenticated state
    else:
        st.error("Login failed. Please check your username and password.")

def process_logout():
    # Assuming UUID and username are in session state
    if "authenticated" in st.session_state and st.session_state["authenticated"]:
        username = st.session_state.get("username")
        user_uuid = st.session_state.get("uuid")  # Retrieve UUID for logging
        if username and user_uuid:
            log_activity(username, user_uuid, "logout")  # Include UUID in log

        # Clear session state or reset specific keys related to user session
        for key in list(st.session_state.keys()):
            del st.session_state[key]

        st.rerun()  # Refresh the app to reflect the logout state
    else:
        print("User is not logged in.")

def show_login_page():
    st.markdown("""
        <style>
            .label-font {
                font-size: 21px !important;
                font-weight: bold !important;
                background-color: rgba(255, 255, 255, 0.4); /* Semi-transparent white background for labels */
                border-radius: 10px; /* Rounded corners for labels */
                padding: 5px 10px; /* Padding inside the label for spacing */
                display: inline-block; /* Ensure labels are inline with inputs */
                margin-bottom: 5px; /* Space below the label */
            }
            .stTextInput > div > div > input {
                background-color: rgba(255, 255, 255, 0.4); /* Semi-transparent background for input fields */
                color: #333; /* Color of the text within the input */
                font-size: 16px; /* Consistent font size for all input fields */
                height: 50px; /* Fixed height for the input fields */
                padding: 0 10px; /* Consistent padding inside the input fields */
                border-radius: 5px; /* Rounded corners for the input fields */
            }
            .button-container {
                display: flex;
                justify-content: center; /* Centering the container horizontally */
                align-items: center; /* Aligning items vertically */
                margin-top: 20px;
            }
            .new-user-text {
                font-size: 18px !important; /* Increased font size */
                font-weight: bold;
                margin-right: 10px; /* Right margin for spacing */
                background-color: rgba(255, 255, 255, 0.5); /* Semi-translucent white background */
                padding: 5px 5px; /* Padding inside the background */
                border-radius: 5px; /* Rounded corners for background */
                display: inline-block; /* Ensure the background wraps the text */
            }
            button {
                background-color: #4CAF50; /* Green background */
                color: white;
                border: none;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 10px;
                margin: 4px 2px;
                transition-duration: 0.4s;
                cursor: pointer;
                border-radius: 8px; /* Rounded corners */
            }
            button:hover {
                background-color: #7FFFD4;
            }
        </style>
        """, unsafe_allow_html=True)

    with st.form("login_form"):
        st.markdown('<p class="label-font">Username</p>', unsafe_allow_html=True)
        username = st.text_input("Username", key="login_username", label_visibility="collapsed")
        st.markdown('<p class="label-font">Password</p>', unsafe_allow_html=True)
        password = st.text_input("Password", type="password", key="login_password", label_visibility="collapsed")
        login_submitted = st.form_submit_button("Login")

    col1, col2 = st.columns([1, 2], gap="small")
    with col1:
        st.markdown('<div class="new-user-text">New User?</div>', unsafe_allow_html=True)
    with col2:
        if st.button("Create an Account"):
            st.session_state.show_registration = True
            st.rerun()

    if login_submitted:
        authenticated, user_uuid = login_user(username, password)
        if authenticated:
            st.session_state["authenticated"] = True
            st.session_state["username"] = username  # Set username in session state
            st.session_state["uuid"] = user_uuid  # Set user_uuid in session state
            st.rerun()
        else:
            st.error("Incorrect username or password.")

def show_registration_page():
    # Custom CSS to style labels, input fields, and buttons
    st.markdown("""
        <style>
            .label-font {
                font-size: 21px !important;
                font-weight: bold !important;
                background-color: rgba(255, 255, 255, 0.4); /* Semi-transparent white background for labels */
                border-radius: 10px; /* Rounded corners for labels */
                padding: 5px 10px; /* Padding inside the label for spacing */
                display: inline-block; /* Ensure labels are inline with inputs */
                margin-bottom: 5px; /* Space below the label */
            }
            .stTextInput > div > div > input {
                background-color: rgba(255, 255, 255, 0.4); /* Semi-transparent background for input fields */
                color: #333; /* Color of the text within the input */
                font-size: 16px; /* Consistent font size for all input fields */
                height: 50px; /* Fixed height for the input fields */
                padding: 0 10px; /* Consistent padding inside the input fields */
                border-radius: 5px; /* Rounded corners for the input fields */
            }
            .button-container {
                display: flex;
                justify-content: center; /* Centering the container horizontally */
                align-items: center; /* Aligning items vertically */
                margin-top: 20px;
            }
            .new-user-text {
                font-size: 18px !important; /* Increased font size */
                font-weight: bold;
                margin-right: 10px; /* Right margin for spacing */
                background-color: rgba(255, 255, 255, 0.5); /* Semi-translucent white background */
                padding: 5px 5px; /* Padding inside the background */
                border-radius: 5px; /* Rounded corners for background */
                display: inline-block; /* Ensure the background wraps the text */
            }
            button {
                background-color: #4CAF50; /* Green background */
                color: white;
                border: none;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 10px;
                margin: 4px 2px;
                transition-duration: 0.4s;
                cursor: pointer;
                border-radius: 8px; /* Rounded corners */
            }
            button:hover {
                background-color: #7FFFD4;
            }
        </style>
        """, unsafe_allow_html=True)

    # Start the registration form
    with st.form("registration_form"):
        # Display the username and password fields with label styling
        st.markdown('<p class="label-font">Choose your username</p>', unsafe_allow_html=True)
        username = st.text_input("", key="register_username", label_visibility="collapsed")
        st.markdown('<p class="label-font">Choose your password</p>', unsafe_allow_html=True)
        password = st.text_input("", type="password", key="register_password", label_visibility="collapsed")
        
        # Submit button for the form
        submitted = st.form_submit_button("Create account")

    # Check if the form was submitted and process registration
    if submitted:
        process_registration(username, password)
        
    # Place a container for the "Already Registered?" prompt and "Login Page" button
    with st.container():
        col1, col2 = st.columns([1, 2], gap="small")
        with col1:
            st.markdown('<div class="new-user-text">Already Registered?</div>', unsafe_allow_html=True)
        with col2:
            if st.button("Login Page"):
                # Clear the session state and rerun to display the login page
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.session_state['show_login'] = True
                st.rerun()

def username_exists(username):
    # Check your user database to see if the username exists
    # Return True if it does, False otherwise
    user = db.users.find_one({"username": username})  # Assuming `db` is your database client
    return user is not None
