import streamlit as st
import pandas as pd

# Ruta del archivo Excel original
excel_file_path = "excel/WEBSITE_JP1.xlsm"
sheet_name = "DATA"

# Leer los datos del archivo Excel
@st.cache_data
def load_data():
    df = pd.read_excel(excel_file_path, sheet_name=sheet_name, engine="openpyxl")
    return df

# Inicializar estado de sesión
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

if "data" not in st.session_state:
    st.session_state.data = load_data()

st.title("DATA Sheet - Aroma Depot")

# Botón para activar modo edición
if not st.session_state.edit_mode:
    password = st.text_input("Enter password to enable editing:", type="password")
    if password == "1212":
        st.session_state.edit_mode = True
        st.success("Edit mode enabled.")

# Mostrar los datos editables
if st.session_state.edit_mode:
    edited_df = st.data_editor(st.session_state.data, num_rows="dynamic")
    if st.button("Save"):
        st.session_state.data = edited_df
        st.session_state.edit_mode = False
        st.success("Changes saved to app memory and edit mode disabled.")
else:
    st.dataframe(st.session_state.data)
