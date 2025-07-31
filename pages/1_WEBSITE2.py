import streamlit as st
import pandas as pd
import openpyxl
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from st_aggrid.shared import JsCode

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="WEBSITE2 Pricing", layout="wide")

EXCEL_PATH = "C:/Users/Jorge/OneDrive/Desktop/WebApp/excel/WEBSITE_JP1.xlsm"
sheet_data = openpyxl.load_workbook(EXCEL_PATH, data_only=True)["DATA"]
sheet_list = openpyxl.load_workbook(EXCEL_PATH, data_only=True)["LIST"]

# --- SESIÓN ---
for key in ["lock_tax", "lock_discount", "lock_profit", "lock_shipping", "lock_search"]:
    if key not in st.session_state:
        st.session_state[key] = False

# --- PRODUCT LIST ---
product_list = [str(cell.value) for cell in sheet_list["A"][1:1900] if cell.value]
selected_product = st.selectbox("🔍 Search Product", product_list)

# --- BUSCAR DATOS ---
def buscar_datos_producto(producto):
    for row in sheet_data.iter_rows(min_row=2):
        if str(row[0].value).strip() == str(producto).strip():
            precio_oil = row[1].value
            labor_costs = [cell.value for cell in row[2:14]]
            return precio_oil, labor_costs
    return 0.0, [0.0]*12

precio_oil, labor_costs = buscar_datos_producto(selected_product)

# --- FRANJA VERDE ---
st.markdown(f"<div style='background-color:#a3d9a5;padding:10px;border-radius:5px;text-align:center;'><b>💲 Price per Pound: ${precio_oil:.2f}</b></div>", unsafe_allow_html=True)

# --- SUBMENÚ ---
st.markdown("### 🧾 Submenú empresarial")
col1, col2, col3, col4 = st.columns(4)
with col1:
    tax = st.number_input("Tax %", value=12.64, step=0.1, disabled=st.session_state.lock_tax, format="%.2f")
    st.checkbox("🔒", key="lock_tax")
with col2:
    discount = st.number_input("Discount %", value=0.0, step=0.1, disabled=st.session_state.lock_discount, format="%.2f")
    st.checkbox("🔒", key="lock_discount")
with col3:
    fee_website = st.number_input("Fee Website", value=4.2, step=0.1, disabled=False, format="%.2f")
with col4:
    suggested_profit = st.number_input("Suggested Profit %", value=75.0, step=0.1, disabled=st.session_state.lock_profit, format="%.2f")
    st.checkbox("🔒", key="lock_profit")

# --- DATOS BASE ---
sizes = ["1 OZ", "2 OZ", "4 OZ", "8 OZ", "1 LB", "2 LB", "4 LB", "8 LB",
         "1 OZ SPRAY", "2 OZ SPRAY", "10 ML", "30 ML"]
default_shipping = [4.71, 4.71, 4.71, 5.03, 8.86, 9.20, 9.20, 16.85,
                    4.71, 4.71, 4.71, 4.71]

df = pd.DataFrame({
    "Size": sizes,
    "Labor to Make": labor_costs,
    "Shipping": default_shipping,
    "Price": [10.00]*12,
    "Discount": [0.00]*12,
    "Price with Discount": [0.00]*12,
    "Tax": [0.00]*12,
    "Price + Tax": [0.00]*12,
    "Fee Website": [0.00]*12,
    "Profit": [0.00]*12,
    "Total Profit": [0.00]*12,
    "Search %": [0.00]*12,
    "Suggested Price": [0.00]*12,
    "✔️": [False]*12
})

# --- CÁLCULOS ---
df["Discount"] = df["Price"] * (discount / 100)
df["Price with Discount"] = df["Price"] - df["Discount"]
df["Tax"] = df["Price"] * (tax / 100)
df["Price + Tax"] = df["Price"] + df["Tax"]
df["Fee Website"] = df["Price"] * (fee_website / 100)
df["Profit"] = df["Price"] - df["Shipping"] - df["Labor to Make"] - df["Discount"] - df["Fee Website"]
df["Total Profit"] = (df["Profit"] / df["Labor to Make"]).replace([float("inf"), -float("inf")], 0)
df["Suggested Price"] = df["Labor to Make"] * (1 + suggested_profit / 100) + df["Shipping"]

# --- AGGRID CONFIG ---
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_columns(["Shipping", "Search %"], editable=not st.session_state.lock_shipping)
gb.configure_columns(["Price"], editable=True)
gb.configure_columns(["✔️"], cellEditor='agCheckboxCellEditor', editable=True)
gb.configure_columns(["Tax", "Fee Website", "Profit", "Total Profit", "Suggested Price", "Price + Tax", "Price with Discount", "Discount"], type=["numericColumn"], valueFormatter='x.toLocaleString("en-US", {style: "currency", currency: "USD"})')
gb.configure_columns(["Search %"], type=["numericColumn"], valueFormatter='x.toFixed(2) + "%"')
grid_options = gb.build()

# --- BOTÓN PRICE ---
if st.button("💰 PRICE"):
    df["Price"] = df["Suggested Price"]
    st.success("✔️ Suggested Price copiado a columna Price.")

# --- TABLA ---
st.markdown("### 📊 Tabla de precios")
AgGrid(df, gridOptions=grid_options, update_mode=GridUpdateMode.VALUE_CHANGED, height=600, fit_columns_on_grid_load=True)