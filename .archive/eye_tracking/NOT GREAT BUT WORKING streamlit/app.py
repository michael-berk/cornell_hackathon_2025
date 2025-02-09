import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

st.title("WebGazer.js Eye Tracking in Streamlit")

# Load the HTML file inside Streamlit
with open("webgazer_component.html", "r") as f:
    html_code = f.read()

components.html(html_code, height=600, width=1000)
