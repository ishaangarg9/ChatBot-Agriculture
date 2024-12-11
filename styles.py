background_image_url = "https://ideogram.ai/api/images/direct/AqHNRuHHSU-HTtHCVHaRuQ.png"

chat_message_styles = f"""
<style>
    .stApp {{
        background-image: url('{background_image_url}');
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        font-family: 'Arial', sans-serif;
    }}

    /* Fade-in animation for chat messages */
    @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}

    .chat-message {{
        display: flex;
        align-items: center;
        margin-bottom: 10px;
        animation: fadeIn 0.5s; /* Apply the fade-in animation */
    }}

    /* Scale animation for avatars on hover */
    .avatar {{
        width: 40px;
        height: 40px;
        border-radius: 20px;
        margin-right: 10px;
        transition: transform 0.2s; /* Smooth transition for scaling */
    }}
    .avatar:hover {{
        transform: scale(1.1); /* Slightly increase the size on hover */
    }}

    /* Styles for user and AI avatars */
    .user-avatar .avatar, .ai-avatar .avatar {{
        /* Additional styles if needed */
    }}

    .message-text {{
        background-color: #f0f0f0;
        border-radius: 15px;
        padding: 10px;
        margin: 0;
    }}

    /* Hover effect for buttons */
    button {{
        transition: background-color 0.2s, box-shadow 0.2s; /* Smooth transition for background and shadow */
    }}
    button:hover {{
        background-color: #e7e7e7; /* Lighter shade on hover */
        box-shadow: 0 2px 5px rgba(0,0,0,0.2); /* Slight shadow for depth */
    }}

    /* Adjustments for mobile responsiveness */
    @media (max-width: 768px) {{
        .stApp {{
            background-attachment: scroll;
        }}
    }}
</style>
"""

# Ensure to apply this CSS with st.markdown(chat_message_styles, unsafe_allow_html=True) 
# in your Streamlit app to activate the styling.
