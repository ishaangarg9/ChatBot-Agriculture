# AgriBot 🌾

AgriBot is a Streamlit-based chatbot designed to assist farmers with various queries related to farming. The chatbot provides information on weather forecasts, crop rotation advice, pest management tips, best planting times, and organic farming practices. It features user authentication, audio transcription, and chat history logging using MongoDB.

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [FFmpeg Installation](#ffmpeg-installation)
- [File Overview](#file-overview)
  - [main.py](#mainpy)
  - [chat.py](#chatpy)
  - [auth.py](#authpy)
  - [utils.py](#utilspy)
  - [styles.py](#stylespy)
  - [user_manage.py](#user_managepy)
- [Usage](#usage)
- [Contact](#contact)

## Features
- User Authentication (Registration and Login)
- Chat Interface with Quick Prompts
- Audio Transcription using Whisper
- Chat History Logging (MongoDB and local JSON files)
- Responsive UI with Custom Styles

## Requirements
- Python 3.8+
- Streamlit
- Whisper
- pymongo
- bcrypt
- requests
- streamlit-chat
- audio-recorder-streamlit

## Installation

### Setting Up a Virtual Environment

1. **Create a virtual environment**:
   ```bash
   python -m venv env
   ```

2. **Activate the virtual environment**:
   - On Windows:
     ```bash
     .\env\Scripts ctivate
     ```
   - On macOS and Linux:
     ```bash
     source env/bin/activate
     ```

3. **Install the required packages**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   streamlit run main.py
   ```

## FFmpeg Installation
The ffmpeg is a cross-platform & open-source software utility to record, convert and stream video/audio files. It can be used to:

- Change the format of a video/audio file
- Extract audio from a video file
- Merge audio and video streams
- Change the bitrate of a video/audio file
- Create GIF from a video file
- Extract still images from a video file
- Embed subtitles into a video file
- Compress or resize a video/audio file
- Record a live stream

### Installing FFmpeg on Windows:
Follow the below steps to install FFmpeg on Windows:

1. **Download the zip file**:
   - Go to the official FFmpeg [download page](https://ffmpeg.org/download.html).
   - Download the zip file of the latest version (As of September 2021, version 4.4 is the latest).

2. **Extract the zip file**:
   - Extract the downloaded zip file to a folder of your choice, for example, `C:fmpeg`.

3. **Add FFmpeg to the system path**:
   - Open the Start menu, search for "Environment Variables," and select "Edit the system environment variables."
   - In the System Properties window, click on the "Environment Variables" button.
   - In the Environment Variables window, under the "System variables" section, find the `Path` variable and select it. Click on "Edit."
   - In the Edit Environment Variable window, click on "New" and add the path to the `bin` folder inside the extracted FFmpeg folder, for example, `C:fmpegin`.
   - Click "OK" to close all windows.

4. **Verify the installation**:
   - Open Command Prompt and type `ffmpeg -version`. If the installation was successful, you should see the version information of FFmpeg.

## File Overview

### main.py
- **Purpose**: The main entry point of the application.
- **Functions**:
  - `handle_prompt(option)`: Handles user prompts.
  - `show_chat_interface()`: Displays the chat interface with different options.
  - `main()`: Sets up the Streamlit page, checks user authentication, and displays either the chat interface or the login/registration page.

### chat.py
- **Purpose**: Manages the chat functionality and interaction with the Whisper model and external APIs.
- **Functions**:
  - `ensure_user_database_exists()`: Ensures the existence of the user database directory.
  - `query(payload)`: Sends a query to the Hugging Face API with the conversation history and user prompt to get a response from the AI model.
  - `load_whisper_model()`: Loads the Whisper model for audio transcription to avoid reloading it on each call.
  - `transcribe_audio(audio_file_path)`: Transcribes audio files using the Whisper model.
  - `transcribe_audio_or_use_text_input(audio_data, text_input)`: Handles both audio and text input, converting audio files to text using the Whisper model.
  - `object_id_converter(o)`: Converts MongoDB ObjectId to a JSON serializable format.
  - `save_chat_history(user_message, assistant_message, username)`: Saves chat history to MongoDB and a local JSON file, ensuring the directory and necessary paths exist.
  - `reset_session_state()`: Resets session state variables, except for authentication and username.
  - `reset_conversation_state()`: Specifically resets conversation history and related session state variables.
  - `display_quick_prompts()`: Displays a set of quick prompt options for the user, associating each with an icon.
  - `handle_user_input(input_text)`: Handles user input, displays the query and bot response in the chat interface, and saves the conversation history.
  - `chat_interface()`: Manages the main chat interface, checking user authentication and handling various input types (text, uploaded audio, recorded audio).

### auth.py
- **Purpose**: Manages user authentication and registration.
- **Functions**:
  - `get_database()`: Connects to the MongoDB database.
  - `hash_password(password)`: Hashes passwords.
  - `register_user(username, password, user_uuid)`: Registers a new user.
  - `process_registration(username, password)`: Processes user registration.
  - `login_user(username, password)`: Logs in a user.
  - `log_activity(username, uuid, action)`: Logs user activities.
  - `process_login(username, password)`: Processes user login.
  - `process_logout()`: Processes user logout.
  - `show_login_page()`: Displays the login page.
  - `show_registration_page()`: Displays the registration page.
  - `username_exists(username)`: Checks if a username exists in the database.

### utils.py
- **Purpose**: Provides utility functions for the application.
- **Functions**:
  - `ensure_user_database_exists()`: Ensures the existence of the user database directory.
  - `get_database()`: Connects to the MongoDB database.
  - `hash_password(password)`: Hashes passwords.
  - `verify_password(stored_password, provided_password)`: Verifies passwords.

### styles.py
- **Purpose**: Contains custom CSS styles for the Streamlit application.
- **Styles**:
  - Background styling.
  - Chat message animations.
  - Avatar styling and hover effects.
  - Button hover effects.
  - Mobile responsiveness.

### user_manage.py
- **Purpose**: Manages user registration, login, and activity logging using local JSON files.
- **Functions**:
  - `load_json(filename)`: Loads JSON data from a file.
  - `save_json(filename, data)`: Saves data to a JSON file.
  - `register_user(username, password)`: Registers a new user.
  - `login_user(username, password)`: Logs in a user.
  - `log_activity(username, action)`: Logs user activities.

## Usage
1. Open your terminal and navigate to the project directory.
2. Activate the virtual environment:
   - On Windows:
     ```bash
     .\env\Scripts ctivate
     ```
   - On macOS and Linux:
     ```bash
     source env/bin/activate
     ```
3. Run the application using Streamlit:
   ```bash
   streamlit run main.py
   ```
4. Open the provided URL in your web browser.
5. Register a new user or log in with existing credentials.
6. Use the chat interface to interact with AgriBot, ask questions, and receive farming advice.


