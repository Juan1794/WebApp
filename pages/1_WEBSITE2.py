import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    return pd.read_excel("excel/WEBSITE_JP1.xlsm", sheet_name="DATA")

@st.cache_data
def load_list():
    df_list = pd.read_excel("excel/WEBSITE_JP1.xlsm", sheet_name="LIST")
    return df_list.iloc[:, 0].dropna().unique().tolist()

df_data = load_data()
product_options = load_list()

st.set_page_config(layout="wide", page_title="PRODUCT MANAGER - WEBSITE2")
st.markdown("<h1 style='font-weight: bold;'>📦 PRODUCT MANAGER - WEBSITE2</h1>", unsafe_allow_html=True)

col1, col3, col4 = st.columns([3, 1.5, 1.5])
with col1:
    product_name = st.selectbox("🔍 Search Product", [""] + product_options)
with col3:
    tax_percent = st.number_input("🧾 Tax %", format="%.2f", value=8.00)
with col4:
    discount_percent = st.number_input("💸 Discount %", format="%.2f", value=0.00)

suggested_profit = st.number_input("🔥 Suggested Profit %", format="%.2f", value=20.00)

if product_name:
    row = df_data[df_data.iloc[:, 0].str.lower() == product_name.lower()]
    if not row.empty:
        price_from_data = float(row.iloc[0, 1])
        st.success(f"Price per Pound found: ${price_from_data:.2f}")

        sizes = ["1 OZ", "2 OZ", "4 OZ", "8 OZ", "1 LB", "2 LB", "4 LB", "8 LB",
                 "1 OZ SPRAY", "2 OZ SPRAY", "10 ML", "30 ML"]
        labor_cols = list(range(2, 14))

        rows = []
        for i, size in enumerate(sizes):
            labor = float(row.iloc[0, labor_cols[i]]) if i < len(labor_cols) else 0.00
            shipping = 0.00
            price = price_from_data
            discount = price * discount_percent / 100
            tax = price * tax_percent / 100
            price_plus_tax = price + tax
            fee = price * (4.2 * (100 + tax_percent) / 100) / 100
            profit = price - shipping - labor - fee - discount
            total_profit = (profit / labor) if labor > 0 else 0
            search_percent = suggested_profit
            suggested_price = round((price + (price * search_percent / 100) + shipping) /
                                    (1 - ((discount_percent + 4.2 * (100 + tax_percent) / 100) / 100)), 2)
            price_with_discount = price - discount if discount > 0 else "A&D"
            rows.append([size, labor, shipping, price, price_with_discount, tax, price_plus_tax,
                         fee, discount, profit, total_profit, search_percent / 100, suggested_price, False])

        columns = ["Size", "Labor to Make", "Shipping", "Price", "Price with Discount", "Tax", "Price+Tax",
                   "Fee Website", "Discount", "Profit", "Total Profit", "Search %", "Suggested Price", "✔"]
        df = pd.DataFrame(rows, columns=columns)

        colB1, colB2 = st.columns(2)
        with colB1:
            if st.button("💲 APPLY PRICE"):
                df["Price"] = df["Suggested Price"]
                df["Price with Discount"] = df.apply(lambda x: x["Price"] - x["Discount"] if x["Discount"] > 0 else "A&D", axis=1)

        with colB2:
            if st.button("🚀 SEND WEB"):
                selected = df[df["✔"] == True]
                if not selected.empty:
                    st.success("Products sent to WOOCOMMERCE_SALE (simulado).")
                else:
                    st.warning("No products selected.")

        def highlight(val, col_name):
            if col_name == "Size" and val in sizes:
                return 'background-color: #ccffcc; font-weight: bold'
            elif col_name in ["Size", "Labor to Make", "Shipping", "Price", "Price with Discount", "Tax", "Price+Tax",
                              "Fee Website", "Discount", "Profit", "Total Profit", "Search %", "Suggested Price"]:
                return 'background-color: #ffff99; font-weight: bold'
            elif col_name == "Price with Discount" and val == "A&D":
                return 'background-color: red; color: white; font-weight: bold'
            else:
                return ''

        styled_df = df.style.applymap(lambda val: highlight(val, col), subset=pd.IndexSlice[:, df.columns])
        styled_df = styled_df.format({
            "Labor to Make": "${:,.2f}",
            "Shipping": "${:,.2f}",
            "Price": "${:,.2f}",
            "Tax": "${:,.2f}",
            "Price+Tax": "${:,.2f}",
            "Fee Website": "${:,.4f}",
            "Discount": "${:,.2f}",
            "Profit": "${:,.2f}",
            "Total Profit": "{:,.2f}",
            "Search %": "{:.2%}",
            "Suggested Price": "${:,.2f}"
        })

        st.data_editor(
            df,
            column_config={"✔": st.column_config.CheckboxColumn("✔")},
            hide_index=True,
            use_container_width=True,
            num_rows="fixed"
        )
    else:
        st.error("❌ Product not found in DATA.")