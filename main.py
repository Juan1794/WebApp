import streamlit as st
import base64

def set_background():
    image_files = ["AMBER1.jpg", "MORINGA.jpg"]
    for img_path in image_files:
        try:
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
                    </style>
                """, unsafe_allow_html=True)
                break
        except FileNotFoundError:
            continue

set_background()

st.title("Sistema Profesional - Aroma Depot")
st.markdown("## Hoja WEBSITE2")