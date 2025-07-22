import streamlit as st
import pandas as pd
import openpyxl

st.set_page_config(layout="wide", page_title="📦 PRODUCT MANAGER - WEBSITE2")

# ======== CARGA DE DATOS ===========
@st.cache_data
def load_data():
    return pd.read_excel("excel/WEBSITE_JP1.xlsm", sheet_name="DATA")

@st.cache_data
def load_list():
    df_list = pd.read_excel("excel/WEBSITE_JP1.xlsm", sheet_name="LIST")
    return df_list.iloc[:, 0].dropna().unique().tolist()

product_list = load_list()
df_data = load_data()

# ======= FUNCIONES ===========
def buscar_precio(producto):
    row = df_data[df_data["PRODUCT NAME"] == producto]
    return row.iloc[0, 1] if not row.empty else 0.00

def obtener_labor(producto):
    row = df_data[df_data["PRODUCT NAME"] == producto]
    return row.iloc[0, 2:14].values if not row.empty else [0.00]*12

def guardar_datos_woocommerce(data):
    wb = openpyxl.load_workbook("excel/WEBSITE_JP1.xlsm", keep_vba=True)
    ws = wb["WOOCOMMERCE_SALE"]
    next_row = ws.max_row + 1
    for row in data:
        ws.cell(row=next_row, column=1).value = row["Size"]
        ws.cell(row=next_row, column=2).value = row["Product"]
        ws.cell(row=next_row, column=3).value = row["Price"]
        next_row += 1
    wb.save("excel/WEBSITE_JP1.xlsm")

# ======= INTERFAZ ========
st.markdown("<h1 style='font-weight: bold;'>📦 PRODUCT MANAGER - WEBSITE2</h1>", unsafe_allow_html=True)
col1, col2 = st.columns([3, 1])
with col1:
    selected_product = st.selectbox("🔍 Search Product", [""] + list(product_list))
with col2:
    price_per_pound = buscar_precio(selected_product)

if selected_product:
    labor_values = obtener_labor(selected_product)
    sizes = ["1 OZ", "2 OZ", "4 OZ", "8 OZ", "1 LB", "2 LB", "4 LB", "8 LB", "1 OZ SPRAY", "2 OZ SPRAY", "10 ML", "30 ML"]
    df_table = pd.DataFrame({
        "Size": sizes,
        "Labor to Make": labor_values,
        "Shipping": [0.0]*12,
        "Price": [0.0]*12,
        "Price with Discount": [0.0]*12,
        "Tax": [0.0]*12,
        "Price + Tax": [0.0]*12,
        "Fee Website": [0.0]*12,
        "Discount": [0.0]*12,
        "Profit": [0.0]*12,
        "Total Profit": [0.0]*12,
        "Search %": [0.0]*12,
        "Suggested Price": [0.0]*12,
        "Send?": [False]*12
    })

    # ======= PARAMETROS GLOBALES =======
    col_g1, col_g2, col_g3, col_g4 = st.columns(4)
    with col_g1:
        tax = st.number_input("Tax %", value=12.63, step=0.01)
    with col_g2:
        discount = st.number_input("Discount %", value=0.00, step=0.01)
    with col_g3:
        suggested_profit = st.number_input("Suggested Profit %", value=60.00, step=0.01)
    with col_g4:
        website_fee = st.number_input("Website Fee %", value=4.20, step=0.01)

    # ======= INGRESO MANUAL Y CÁLCULOS ========
    st.write("### Tabla de Cálculo Empresarial")
    updated_rows = []
    for i in range(len(df_table)):
        row = df_table.loc[i]
        col1, col2, col3, col4, col5, col6, col7 = st.columns([1.2]*7)
        with col1:
            st.write(row["Size"])
        with col2:
            st.write(f"${row['Labor to Make']:.2f}")
        with col3:
            shipping = st.number_input(f"Shipping {i}", value=0.00, key=f"shipping_{i}")
        with col4:
            price = st.number_input(f"Price {i}", value=0.00, key=f"price_{i}")
        with col5:
            search_pct = st.number_input(f"Search % {i}", value=0.00, key=f"search_{i}")
        with col6:
            send_row = st.checkbox("✅", key=f"send_{i}")
        with col7:
            pass

        discount_amt = price * (discount / 100)
        price_discount = price - discount_amt if discount > 0 else "A&D"
        tax_amt = price * (tax / 100)
        price_tax = price + tax_amt
        fee_amt = price * (website_fee * (1 + tax / 100)) / 100
        profit = price - shipping - row["Labor to Make"] - fee_amt - discount_amt
        total_profit = profit / row["Labor to Make"] if row["Labor to Make"] != 0 else "-"
        formula_hidden_f = row["Labor to Make"] + (row["Labor to Make"] * (search_pct / 100 if search_pct > 0 else suggested_profit / 100)) + shipping
        suggested_price = formula_hidden_f / (1 - ((discount / 100) + (website_fee * (1 + tax / 100) / 100))) if row["Labor to Make"] != 0 else 0.00

        df_table.at[i, "Shipping"] = shipping
        df_table.at[i, "Price"] = price
        df_table.at[i, "Price with Discount"] = price_discount
        df_table.at[i, "Tax"] = tax_amt
        df_table.at[i, "Price + Tax"] = price_tax
        df_table.at[i, "Fee Website"] = fee_amt
        df_table.at[i, "Discount"] = discount_amt
        df_table.at[i, "Profit"] = profit
        df_table.at[i, "Total Profit"] = total_profit
        df_table.at[i, "Search %"] = search_pct
        df_table.at[i, "Suggested Price"] = suggested_price
        df_table.at[i, "Send?"] = send_row

    # ======= BOTONES FUNCIONALES =======
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("📥 APPLY PRICE (Suggested → Price)"):
            for i in range(len(df_table)):
                df_table.at[i, "Price"] = df_table.at[i, "Suggested Price"]
    with col_b2:
        if st.button("🚀 SEND WEB"):
            data_to_send = []
            for i, row in df_table.iterrows():
                if row["Send?"]:
                    data_to_send.append({
                        "Size": row["Size"],
                        "Product": selected_product,
                        "Price": row["Price"]
                    })
            if data_to_send:
                guardar_datos_woocommerce(data_to_send)
                st.success("✅ Productos enviados a hoja WOOCOMMERCE_SALE.")

    # ======= TABLA FINAL (solo visual) =======
    st.dataframe(df_table.drop(columns=["Send?"]), use_container_width=True)