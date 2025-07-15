import streamlit as st
import base64

def set_background():
    img_path = "AMBER1.jpg"

    with open(img_path, "rb") as img_file:
        img_bytes = img_file.read()
        encoded_img = base64.b64encode(img_bytes).decode()

    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded_img}");
            background-size: cover;
            background-repeat: no-repeat;
            background-position: center;
        }}

        /* CAMBIO FUERTE DEL COLOR DEL SIDEBAR USANDO 'aside' */
        aside[data-testid="stSidebar"] {{
            background-color: #3E2723 !important;
            padding-top: 2rem;
        }}

        aside[data-testid="stSidebar"] * {{
            color: white !important;
        }}
        </style>
    """, unsafe_allow_html=True)

set_background()

st.markdown("""
<div style='text-align: center; padding-top: 100px;'>
    <h1 style='font-size: 50px; color: white;'>Aroma Depot</h1>
    <h3 style='font-size: 28px; color: white;'>Automatic Pricing System</h3>
</div>
""", unsafe_allow_html=True)