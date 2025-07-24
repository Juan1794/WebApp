# 1_WEBSITE2_EXCEL_INTEGRATED_FINAL.py

import streamlit as st
import pandas as pd
import openpyxl

st.set_page_config(layout="wide", page_title="📦 PRODUCT MANAGER - WEBSITE2")

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

# Estados de bloqueo global por columna
for key in ["lock_shipping", "lock_search", "lock_price", "lock_tax", "lock_discount", "lock_profit", "lock_fee"]:
    if key not in st.session_state:
        st.session_state[key] = False

df_data = load_data()
product_list = load_list()

st.markdown("<h1 style='font-weight:bold;'>📦 PRODUCT MANAGER - WEBSITE2</h1>", unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])
with col1:
    selected_product = st.selectbox("🔍 Search Product", [""] + product_list)
with col2:
    price_per_pound = buscar_precio(selected_product)
    st.markdown(f"<span style='background-color:#ccffcc;padding:0.4em;border-radius:6px;'>💲 Price per Pound: <strong>${price_per_pound:.2f}</strong></span>", unsafe_allow_html=True)

# Submenú visual tipo listado
with st.expander("🔒 LOCKED FIELDS", expanded=True):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.session_state.lock_tax = st.toggle("🔒 Tax %", value=st.session_state.lock_tax)
        tax = st.number_input("Tax %", value=12.63, step=0.01, disabled=st.session_state.lock_tax)
    with c2:
        st.session_state.lock_discount = st.toggle("🔒 Discount %", value=st.session_state.lock_discount)
        discount = st.number_input("Discount %", value=0.00, step=0.01, disabled=st.session_state.lock_discount)
    with c3:
        st.session_state.lock_profit = st.toggle("🔒 Profit %", value=st.session_state.lock_profit)
        suggested_profit = st.number_input("Suggested Profit %", value=60.00, step=0.01, disabled=st.session_state.lock_profit)
    with c4:
        st.session_state.lock_fee = st.toggle("🔒 Website Fee %", value=st.session_state.lock_fee)
        website_fee = st.number_input("Website Fee %", value=4.20, step=0.01, disabled=st.session_state.lock_fee)

# TABLA UNIFICADA (TODO DENTRO)
if selected_product:
    sizes = ["1 OZ", "2 OZ", "4 OZ", "8 OZ", "1 LB", "2 LB", "4 LB", "8 LB", "1 OZ SPRAY", "2 OZ SPRAY", "10 ML", "30 ML"]
    labor_values = obtener_labor(selected_product)

    data = []
    for i in range(12):
        data.append({
            "Size": sizes[i],
            "Labor to Make": round(labor_values[i], 2),
            "Shipping": 0.00,
            "Price": 0.00,
            "Search %": 0.00
        })

    df_edit = pd.DataFrame(data)

    edited = st.data_editor(
        df_edit,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Shipping": st.column_config.NumberColumn(format="$%.2f", disabled=st.session_state.lock_shipping),
            "Price": st.column_config.NumberColumn(format="$%.2f", disabled=st.session_state.lock_price),
            "Search %": st.column_config.NumberColumn(format="%.2f%%", disabled=st.session_state.lock_search),
        },
        num_rows="fixed"
    )

    # Calcular resultados por fila
    results = []
    for i, row in edited.iterrows():
        labor = row["Labor to Make"]
        shipping = row["Shipping"]
        price = row["Price"]
        search = row["Search %"]

        discount_amt = round(price * (discount / 100), 2)
        tax_amt = round(price * (tax / 100), 2)
        fee_amt = round(price * (website_fee * (1 + tax / 100)) / 100, 2)
        price_tax = round(price + tax_amt, 2)
        price_discount = round(price - discount_amt, 2) if discount > 0 else "A&D"
        profit = round(price - shipping - labor - fee_amt - discount_amt, 2)
        total_profit = f"{profit / labor:.2%}" if labor != 0 else "-"
        base = labor + (labor * ((search / 100) if search > 0 else (suggested_profit / 100))) + shipping
        suggested_price = round(base / (1 - ((discount / 100) + (website_fee * (1 + tax / 100) / 100))), 2) if labor != 0 else 0.00

        results.append({
            "Size": row["Size"],
            "Labor to Make": f"${labor:.2f}",
            "Shipping": f"${shipping:.2f}",
            "Price": f"${price:.2f}",
            "Search %": f"{search:.2%}",
            "Discount": f"${discount_amt:.2f}",
            "Tax": f"${tax_amt:.2f}",
            "Fee Website": f"${fee_amt:.2f}",
            "Price + Tax": f"${price_tax:.2f}",
            "Price with Discount": price_discount,
            "Profit": f"${profit:.2f}",
            "Total Profit": total_profit,
            "Suggested Price": f"${suggested_price:.2f}"
        })

    st.markdown("### 📊 Final Calculation Table")
    st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)