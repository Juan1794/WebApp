import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="🛒 WOOCOMERCE FILE", layout="wide")
st.title("🛒 WOOCOMERCE FILE - Editor de Productos para WooCommerce")

# Ruta del archivo Excel y nombre de la hoja
excel_file = "excel/WEBSITE_JP1.xlsm"  # Asegúrate que este archivo esté en la carpeta /excel
sheet_name = "WOOCOMERCE_FILE"

# Leer la hoja
try:
    df = pd.read_excel(excel_file, sheet_name=sheet_name, engine="openpyxl")
    st.dataframe(df, use_container_width=True)
except FileNotFoundError:
    st.error(f"❌ No se encontró el archivo: {excel_file}")
except Exception as e:
    st.error(f"❌ Error al cargar los datos: {e}")