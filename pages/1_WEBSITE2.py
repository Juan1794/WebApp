import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
import openpyxl

st.set_page_config(layout="wide", page_title="📦 WEBSITE2")

@st.cache_data
def load_data():
    return pd.read_excel("excel/WEBSITE_JP1.xlsm", sheet_name="DATA")

@st.cache_data
def load_list():
    df_list = pd.read_excel("excel/WEBSITE_JP1.xlsm", sheet_name="LIST")
    return df_list.iloc[:, 0].dropna().unique().tolist()

def buscar_precio(producto):
    row = df_data[df_data["PRODUCT NAME"] == producto]
    return row.iloc[0, 1] if not row.empty else 0.00

def obtener_labor(producto):
    row = df_data[df_data["PRODUCT NAME"] == producto]
    return row.iloc[0, 2:14].values if not row.empty else [0.00]*12

# Estados persistentes
for key in ["lock_shipping", "lock_search", "df_original"]:
    if key not in st.session_state:
        if key == "df_original":
            st.session_state[key] = None
        else:
            st.session_state[key] = False

df_data = load_data()
product_list = load_list()

st.title("📦 WEBSITE2 FINAL")

col1, col2 = st.columns([4, 1])
with col1:
    selected_product = st.selectbox("🔍 Search Product", [""] + product_list)
with col2:
    price_per_pound = buscar_precio(selected_product)
    st.markdown(f"<div style='background:#cce5cc;padding:10px;border-radius:6px;font-weight:bold;color:green;'>💲 Price per Pound: ${price_per_pound:.2f}</div>", unsafe_allow_html=True)

with st.expander("⚙️ CONFIGURACIÓN", expanded=True):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.checkbox("🔒 Tax %", key="lock_tax")
        tax = st.number_input("Tax %", step=0.01, value=12.63, disabled=st.session_state.get("lock_tax", False))
    with c2:
        st.checkbox("🔒 Discount %", key="lock_discount")
        discount = st.number_input("Discount %", step=0.01, value=0.00, disabled=st.session_state.get("lock_discount", False))
    with c3:
        st.checkbox("🔒 Profit %", key="lock_profit")
        suggested_profit = st.number_input("Suggested Profit %", step=0.01, value=75.00, disabled=st.session_state.get("lock_profit", False))
    with c4:
        st.checkbox("🔒 Website Fee %", key="lock_fee")
        website_fee = st.number_input("Website Fee %", step=0.01, value=4.20, disabled=st.session_state.get("lock_fee", False))

if selected_product:
    sizes = ["1 OZ", "2 OZ", "4 OZ", "8 OZ", "1 LB", "2 LB", "4 LB", "8 LB", "1 OZ SPRAY", "2 OZ SPRAY", "10 ML", "30 ML"]
    labor_values = obtener_labor(selected_product)
    shipping_default = {
        "1 OZ": 4.71, "2 OZ": 4.71, "4 OZ": 4.71, "8 OZ": 5.03, "1 LB": 8.86,
        "2 LB": 9.20, "4 LB": 9.20, "8 LB": 16.85, "1 OZ SPRAY": 4.71,
        "2 OZ SPRAY": 4.71, "10 ML": 4.71, "30 ML": 4.71
    }

    if st.session_state.df_original is None:
        rows = []
        for i, size in enumerate(sizes):
            labor = round(labor_values[i], 2)
            shipping = shipping_default.get(size, 0.00)
            rows.append({
                "Size": size,
                "Labor to Make": labor,
                "Shipping": shipping,
                "Price": 0.00,
                "Search %": 0.00,
                "✔️": False
            })
        st.session_state.df_original = pd.DataFrame(rows)

    def calcular(row):
        labor = row["Labor to Make"]
        shipping = row["Shipping"]
        price = row["Price"]
        search = row["Search %"]
        discount_amt = price * discount / 100
        tax_amt = price * tax / 100
        fee_amt = price * (website_fee * (1 + tax / 100)) / 100
        price_tax = price + tax_amt
        price_discount = "-" if labor == 0 else ("A&D" if discount == 0 else price - discount_amt)
        profit = price - shipping - labor - fee_amt - discount_amt
        total_profit = "-" if labor == 0 else profit / labor
        base = labor + (labor * (search / 100 if search > 0 else suggested_profit / 100)) + shipping
        suggested_price = 0.00 if labor == 0 else base / (1 - ((discount / 100) + (website_fee * (1 + tax / 100) / 100)))
        return pd.Series([
            round(price_discount, 2) if isinstance(price_discount, float) else price_discount,
            round(tax_amt, 2),
            round(price_tax, 2),
            round(fee_amt, 2),
            round(discount_amt, 2),
            round(profit, 2),
            f"{total_profit:.2%}" if isinstance(total_profit, float) else total_profit,
            round(suggested_price, 2)
        ], index=[
            "Price with Discount", "Tax", "Price + Tax", "Fee Website",
            "Discount", "Profit", "Total Profit", "Suggested Price"
        ])

    b1, b2 = st.columns(2)
    with b1:
        st.session_state.lock_shipping = st.toggle("🔒 Shipping", value=st.session_state.lock_shipping)
    with b2:
        st.session_state.lock_search = st.toggle("🔒 Search %", value=st.session_state.lock_search)

    gb = GridOptionsBuilder.from_dataframe(st.session_state.df_original)
    gb.configure_columns(["Shipping"], editable=not st.session_state.lock_shipping, type=["numericColumn"], precision=2)
    gb.configure_columns(["Search %"], editable=not st.session_state.lock_search, type=["numericColumn"], precision=2)
    gb.configure_columns(["Price"], editable=True, type=["numericColumn"], precision=2)
    gb.configure_columns(["✔️"], editable=True, cellEditor='agCheckboxCellEditor')
    gb.configure_columns(["Labor to Make"], editable=False, precision=2)
    grid_options = gb.build()

    response = AgGrid(st.session_state.df_original, gridOptions=grid_options, update_mode=GridUpdateMode.MODEL_CHANGED, fit_columns_on_grid_load=True)
    df_editado = response.data.copy()

    calculado = df_editado.apply(calcular, axis=1)
    for col in calculado.columns:
        df_editado[col] = calculado[col]

    if st.button("📌 PRICE: Copiar Suggested → Price"):
        suggested_values = df_editado["Suggested Price"].copy()
        st.session_state.df_original["Price"] = suggested_values
        df_editado["Price"] = suggested_values

    st.markdown("### 📊 RESULTADO FINAL")
    AgGrid(df_editado, fit_columns_on_grid_load=True, update_mode=GridUpdateMode.NO_UPDATE)