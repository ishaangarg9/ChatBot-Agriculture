import requests
import whisper
import tempfile
import streamlit as st
from streamlit_chat import message
from audio_recorder_streamlit import audio_recorder  # Add this import for audio recording
import json
import datetime
import os
from auth import log_activity, show_login_page
from bson import ObjectId  # Import ObjectId from bson (installed with pymongo)
from utils import get_database


db = get_database()


users_db_path = "user_database/users.json"  # Path for your local JSON file for users
chat_data_path = os.path.join("chat_data", "chat_history.json")  # Path for local chat history storage


def ensure_user_database_exists():
    database_path = "user_database"
    os.makedirs(database_path, exist_ok=True)

def query(payload):
    history_str = " ".join([f"User: {user_msg} , Assistant: {assistant_msg}" for user_msg, assistant_msg in st.session_state.conversation_history])
    headers = {"Authorization":f"Bearer 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"}
    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
    json_body = {
        "inputs": f"[INST] <<SYS>> Your job is to talk like a farming assistant for a farmer. Every response must sound the same. Also, remember the previous conversation {history_str} and answer accordingly <<SYS>> User: {payload} Assistant: [/INST]",
        "parameters": {"max_new_tokens": 4096, "top_p": 0.9, "temperature": 0.7}
    }
    
    response = requests.post(API_URL, headers=headers, json=json_body)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get a valid response: Status code {response.status_code}, Response text: {response.text}")
        return {"error": f"API request failed with status code {response.status_code}"}

def load_whisper_model():
    # Load the Whisper model outside the transcription function to avoid reloading it on each call
    model = whisper.load_model("base")
    return model

# Load the model when the app starts/reloads
model = load_whisper_model()

def transcribe_audio(audio_file_path):
    global model
    # Perform transcription using the pre-loaded Whisper model
    result = model.transcribe(audio_file_path)
    return result["text"]

# def transcribe_audio_or_use_text_input(audio_data, text_input=None):
#     if audio_data:
#         try:
#             # Write the audio bytes to a temporary file and keep it until transcription is done
#             with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
#                 tmp_audio.write(audio_data)
#                 tmp_audio.flush()  # Ensure all data is written to disk
#                 transcription = transcribe_audio(tmp_audio.name)
#             # Once transcription is done, the file can be safely deleted
#             os.remove(tmp_audio.name)
#             return transcription
#         except Exception as e:
#             st.error(f"Error during audio transcription: {e}")
#             return "Error transcribing audio. Please try again or use text input."
#     else:
#         return text_input

def transcribe_audio_or_use_text_input(audio_data, text_input=None):
    if audio_data:
        try:
            # Check if audio_data is a file-like object with a read() method
            if hasattr(audio_data, 'read'):
                audio_bytes = audio_data.read()
            else:
                audio_bytes = audio_data

            # Write the audio bytes to a temporary file and keep it until transcription is done
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
                tmp_audio.write(audio_bytes)
                tmp_audio.flush()  # Ensure all data is written to disk
                transcription = transcribe_audio(tmp_audio.name)
            # Once transcription is done, the file can be safely deleted
            os.remove(tmp_audio.name)
            return transcription
        except Exception as e:
            st.error(f"Error during audio transcription: {e}")
            return "Error transcribing audio. Please try again or use text input."
    else:
        return text_input

def object_id_converter(o):
    if isinstance(o, ObjectId):
        return str(o)
    raise TypeError(f'Object of type {o.__class__.__name__} is not JSON serializable')

def save_chat_history(user_message, assistant_message, username):
    # Ensure the chat_data directory exists
    chat_data_dir = os.path.dirname(chat_data_path)
    os.makedirs(chat_data_dir, exist_ok=True)
    
    user_uuid = None
    
    # Try to retrieve the user's UUID from MongoDB
    if db is not None:
        user_data = db.users.find_one({"username": username})
        if user_data:
            user_uuid = user_data['uuid']
    
    # If not found in MongoDB, try the local JSON file
    if user_uuid is None and os.path.exists(users_db_path):
        with open(users_db_path, 'r') as file:
            users = json.load(file)
            user_data = users.get(username)
            if user_data:
                user_uuid = user_data.get('uuid')
    
    # If UUID is still not found, log a warning
    if user_uuid is None:
        print(f"Warning: UUID not found for username {username}. Chat history might not be accurately tracked.")
        return

    current_time = datetime.datetime.now().isoformat()
    chat_document = {
        "uuid": user_uuid,
        "user": user_message,
        "assistant": assistant_message,
        "timestamp": current_time
    }

    # Try to insert the chat document into MongoDB
    try:
        db.chat_history.insert_one(chat_document)
        print("Chat history saved successfully in MongoDB.")
    except Exception as e:
        print(f"Failed to save chat history in MongoDB: {e}")

    # Try to append the chat document to the local JSON file
    try:
        chat_history = []
        if os.path.exists(chat_data_path):
            with open(chat_data_path, 'r') as file:
                chat_history = json.load(file)
        chat_history.append(chat_document)
        with open(chat_data_path, 'w') as file:
            json.dump(chat_history, file, default=object_id_converter, indent=4)
        print("Chat history saved successfully in local file.")
    except Exception as e:
        print(f"Failed to save chat history in local file: {e}")
        

def reset_session_state():
    keys_to_delete = [key for key in st.session_state.keys() if key not in ('authenticated', 'username')]
    for key in keys_to_delete:
        del st.session_state[key]

def reset_conversation_state():
    # This function now targets specifically the conversation history and any related keys
    keys_to_delete = ['conversation_history', 'first_query_submitted']
    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]



def display_quick_prompts():
    # Using a dictionary to maintain the order and associate icons
    prompt_options_with_icons = {
        "Weather Forecast": "🌤",
        "Crop Rotation Advice": "🔄",
        "Pest Management Tips": "🐛",
        "Best Planting Times": "🌱",
        "Organic Farming Practices": "🌿"
    }

    # Convert the dictionary into a list adding the default select prompt at the start
    prompt_options = ["Select a quick option..."] + [f"{icon} {option}" for option, icon in prompt_options_with_icons.items()]
    
    # Create a select box with the options
    selected_option = st.selectbox("Quick Options:", options=prompt_options, index=0)

    # Extract just the text part of the option selected by the user
    selected_option_text = selected_option.split(' ', 1)[-1] if selected_option else ""

    # Handle the selected option, ignoring the placeholder and ensuring the option is in the original prompt dictionary
    if selected_option_text in prompt_options_with_icons:
        handle_user_input(selected_option_text)
        st.session_state['first_query_submitted'] = True  # Hide quick prompts after this



def handle_user_input(input_text):
    if input_text:
        # Initialize conversation history if not already done
        if 'conversation_history' not in st.session_state:
            st.session_state['conversation_history'] = []

        # Display the user's query in the chat interface
        message(input_text, is_user=True, key=f"user_{len(st.session_state['conversation_history'])}")

        # Append the user input to the session state for maintaining the conversation history
        st.session_state['conversation_history'].append(("User", input_text))
        st.session_state['first_query_submitted'] = True

        # Payload for the bot API call, adjusted to your model's requirements
        json_body = {
            "inputs": f"Your job is to talk like a farming assistant for a farmer. Every response must sound the same. \nUser: {input_text} Assistant: ",
            "parameters": {"max_new_tokens": 4096, "top_p": 0.9, "temperature": 0.7}
        }

        # Get the bot's response
        response = query(json_body)

        # Process the response and update the conversation history
        try:
            if response and isinstance(response, list) and len(response) > 0:
                assistant_response = response[0].get('generated_text', '').strip()

                # Clean up and display the assistant's response
                if "Assistant: " in assistant_response:
                    assistant_response = assistant_response.split("Assistant: ")[-1]
                assistant_response = assistant_response.replace("[/INST]", "").strip()

                if assistant_response:
                    message(assistant_response, is_user=False, key=f"assistant_{len(st.session_state['conversation_history'])}")
                    st.session_state['conversation_history'].append(("Assistant", assistant_response))

                    # Ensure the username is available in the session state before saving chat history
                    if 'username' in st.session_state:
                        save_chat_history(input_text, assistant_response, st.session_state['username'])
                    else:
                        st.error("Unable to save chat history. Username is not available.")
                else:
                    st.error("No assistant response was found in the API response.")
            else:
                st.error("The response structure is not as expected.")
        except Exception as e:
            st.error(f"An error occurred while processing the response from the assistant: {e}")


def chat_interface():
    st.header("AgriBot 🌾 - Chat")

    # Check if the user is authenticated
    if st.session_state.get("authenticated", False):
        username = st.session_state.get("username", "")
        st.success(f"Hello, {username}! How can I help you today?")

        if 'first_query_submitted' not in st.session_state:
            st.session_state['first_query_submitted'] = False

        if 'conversation_history' not in st.session_state:
            st.session_state['conversation_history'] = []

        # Display existing conversation history
        for idx, (role, msg) in enumerate(st.session_state['conversation_history']):
            if role == "User":
                message(msg, is_user=True, key=f"user_{idx}")
            elif role == "Assistant":
                message(msg, is_user=False, key=f"assistant_{idx}")

        # Display quick prompts if the first query hasn't been submitted
        if not st.session_state['first_query_submitted']:
            display_quick_prompts()

        # Sidebar for input type selection
        input_type = st.sidebar.selectbox("Choose input type:", ["Text", "Upload Audio", "Record Audio"], key='input_type_selection_sidebar')

        # Display the logout button
        show_logout_interface()  # Ensure this function is implemented to handle user logout

        # Input form and handling
        with st.form(key='message_form'):
            user_input = None
            if input_type == "Text":
                user_input = st.text_input("Type your message here:", key="text_input")
            elif input_type == "Upload Audio":
                audio_input = st.file_uploader("Upload an audio file", type=["mp3", "wav", "ogg"], key="audio_uploader")
                if audio_input is not None:
                    user_input = transcribe_audio_or_use_text_input(audio_input)
            elif input_type == "Record Audio":
                # Option to record audio directly in the chat interface
                audio_bytes = audio_recorder(key="audio_recorder")
                # If audio is recorded, display it as an audio player and transcribe it
                if audio_bytes is not None:
                    st.audio(audio_bytes, format="audio/wav")
                    user_input = transcribe_audio_or_use_text_input(audio_bytes)

            # Send button for text, uploaded audio, and recorded audio
            if st.form_submit_button("Send"):
                if user_input:
                    handle_user_input(user_input)

    else:
        # If not authenticated, clear session state and show login page
        st.session_state.clear()
        show_login_page()

            
            
def render_input_form(input_type):
    # Depending on the chosen input type, display the appropriate input widget
    # For text input
    if input_type == "Text":
        user_input = st.text_input("Type your message here:", key="text_input")

    # Logic for handling 'Send' action
    if st.button("Send"):
        handle_user_input(user_input or "")

def render_quick_prompts():
    # Display quick prompts for user convenience
    prompt_options = ["Weather Forecast", "Crop Rotation Advice", "Pest Management Tips", "Best Planting Times", "Organic Farming Practices"]
    for option in prompt_options:
        if st.button(option, key=f"prompt_{option}"):
            handle_user_input(option)

def show_logout_interface():
    # Logout functionality
    if st.sidebar.button("Logout"):
        # Perform logout operations
        st.session_state["authenticated"] = False
        st.rerun()  # Use st.rerun() for consistency

    # Clear Conversation functionality added just below the Logout button
    if st.sidebar.button("Clear Conversation"):
        reset_conversation_state()  # Clear conversation-specific session state
        st.rerun()  # Rerun the app to reflect the changes immediately
