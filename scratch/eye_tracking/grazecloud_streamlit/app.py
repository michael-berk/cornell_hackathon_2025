# pip install streamlit-autorefresh

import streamlit as st
import requests
from streamlit_autorefresh import st_autorefresh

st.set_page_config(layout="wide")
st.title("👀 Gaze Tracking in Streamlit")
st.write("Move your eyes over the words below. The word you're looking at will be highlighted.")

# Define text
phrase = "The quick brown fox jumps over the lazy dog"
words = phrase.split(" ")

# Fetch latest gaze data from the API
def get_gaze_data():
    try:
        response = requests.get("http://127.0.0.1:5000/gaze_data", timeout=1)
        return response.json()
    except requests.exceptions.RequestException:
        return {"x": 0, "y": 0, "word": "None"}

# Auto-refresh every 2 seconds
st_autorefresh(interval=2000, key="gaze_refresh")

# Fetch gaze data
gaze_data = get_gaze_data()
gaze_x, gaze_y = gaze_data["x"], gaze_data["y"]

# Debugging output
st.text(f"Gaze Coordinates: X={gaze_x}, Y={gaze_y}")
print(f"Gaze Coordinates: X={gaze_x}, Y={gaze_y}")

# Display words with gaze detection
highlighted_word = "None"
for word in words:
    if gaze_x % 100 < 50:  # Simulated detection logic
        st.markdown(f"<span style='font-size:30px; background-color:rgba(0, 0, 255, 0.5);'>{word}</span>", unsafe_allow_html=True)
        highlighted_word = word
    else:
        st.markdown(f"<span style='font-size:30px;'>{word}</span>", unsafe_allow_html=True)

# Show highlighted word
st.write(f"Currently looking at: **{highlighted_word}**")
