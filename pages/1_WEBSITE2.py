import streamlit as st
import pandas as pd
from openpyxl import load_workbook

st.set_page_config(page_title="WEBSITE2 - Aroma Depot", layout="wide")

st.markdown("## Página WEBSITE2 - Aroma Depot")
st.markdown("Esta hoja es solo visual. No guarda cambios en el Excel por seguridad.")

ruta_archivo = "./excel/WEBSITE_JP1.xlsm"
hoja_nombre = "WEBSITE2"

try:
    df = pd.read_excel(ruta_archivo, sheet_name=hoja_nombre)
    st.dataframe(df, use_container_width=True)
except Exception as e:
    st.error(f"Error al cargar la hoja '{hoja_nombre}': {e}")