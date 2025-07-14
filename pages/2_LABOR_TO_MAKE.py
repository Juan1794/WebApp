import streamlit as st
import pandas as pd

st.set_page_config(page_title="LABOR TO MAKE", layout="wide")

st.title("🛠️ LABOR TO MAKE - Editor de Costos de Mano de Obra")

excel_file = "excel/WEBSITE_JP1.xlsm"
sheet_name = "LABOR"

try:
    df = pd.read_excel(excel_file, sheet_name=sheet_name, engine="openpyxl")
    st.dataframe(df, use_container_width=True)
except FileNotFoundError:
    st.error(f"❌ No se encontró el archivo: {excel_file}")
except Exception as e:
    st.error(f"❌ Error al cargar los datos: {e}")