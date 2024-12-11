import os
import logging
import bcrypt
from pymongo import MongoClient

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def ensure_user_database_exists():
    database_path = "user_database"
    try:
        # Attempt to create the directory, if it doesn't exist
        os.makedirs(database_path, exist_ok=True)
        logging.info(f"Directory '{database_path}' ensured to exist.")
    except Exception as e:
        # Log any errors encountered during the directory creation
        logging.error(f"Error ensuring directory '{database_path}' exists: {e}")

def get_database():
    CONNECTION_STRING = "mongodb+srv://vikaspedia2024:NMh8eGRLcSf8tSMM@streamlitdb.9eediwg.mongodb.net/?retryWrites=true&w=majority&appName=streamlitDB"
    try:
        conn = MongoClient(CONNECTION_STRING)
        print("Connected successfully!!!")
        return conn.AgriBot
    except:
        print("Could not connect to MongoDB")
        return

def hash_password(password):
    """Hash a password for storing."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    # Ensure the stored password is in bytes format for comparison
    if isinstance(stored_password, str):
        stored_password = stored_password.encode('utf-8')
    
    # Ensure the provided password is in bytes format for comparison
    if isinstance(provided_password, str):
        provided_password = provided_password.encode('utf-8')
    
    # Use bcrypt to check the provided password against the stored hash
    return bcrypt.checkpw(provided_password, stored_password)