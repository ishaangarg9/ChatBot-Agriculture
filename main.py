import streamlit as st
from auth import show_login_page, show_registration_page
from chat import chat_interface,ensure_user_database_exists
from utils import ensure_user_database_exists


def handle_prompt(option):
    # Placeholder function to be filled with logic to handle each prompt
    st.write(f"You selected: {option}")
    # Here, you'd include the logic to fetch or calculate the information requested by the user

def show_chat_interface():
    st.write("Welcome to AgriBot, your personal farming assistant!")
    
    prompt_options = [
        "Tell me about irrigation in both Kharif and Rabi crops",
        "Advice on crop rotation",
        "Pest management tips",
        "Best planting times",
        "Organic farming practices"
    ]
    
    for option in prompt_options:
        if st.button(option):
            handle_prompt(option)


def main():
    ensure_user_database_exists()
    st.set_page_config(page_title="AgriBot", page_icon="🌾", layout="wide")

    # Check if the user is authenticated
    if "authenticated" in st.session_state and st.session_state["authenticated"]:
        # If authenticated, display the chat interface
        chat_interface()
    else:
        # Apply background image for login and registration pages
        background_image_url ="https://ideogram.ai/api/images/direct/AqHNRuHHSU-HTtHCVHaRuQ.png"
        background_style = f"""
        <style>
            .stApp {{
                background-image: url('{background_image_url}');
                background-size: cover;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            .welcome-text {{
                color: #000000; /* Black color */
                background-color: rgba(255, 255, 255, 0.5); /* Translucent white background */
                padding: 2px 5px; /* Reduced padding around the text */
                border-radius: 5px; /* Rounded corners */
                display: inline; /* Align highlight with text */
                margin: 0; /* Remove default margins */
                font-size:50px !important;
                font-weight: bold !important;
            }}
        </style>
        """
        st.markdown(background_style, unsafe_allow_html=True)

        # Login and registration interface
        page_container = st.empty()
        with page_container.container():
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                # Display the logo and welcome text
                st.image("background/logo.png", width=100)
                st.markdown('<div class="welcome-text">Welcome to AgriBot 🌾</div>', unsafe_allow_html=True)

                # Determine which page to display based on session state
                if "show_registration" in st.session_state and st.session_state["show_registration"]:
                    show_registration_page()
                else:
                    show_login_page()

if __name__ == "__main__":
    main()