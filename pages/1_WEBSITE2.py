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

col1, col2, col3, col4 = st.columns([3, 1.3, 1.3, 1.3])
with col1:
    product_name = st.selectbox("🔍 Search Product", [""] + product_options)

# Valores persistentes
if "tax_percent" not in st.session_state:
    st.session_state.tax_percent = 12.63
if "discount_percent" not in st.session_state:
    st.session_state.discount_percent = 0.0
if "suggested_profit" not in st.session_state:
    st.session_state.suggested_profit = 75.0

with col2:
    st.session_state.tax_percent = st.number_input("🧾 Tax %", value=st.session_state.tax_percent, format="%.2f")
with col3:
    st.session_state.discount_percent = st.number_input("💸 Discount %", value=st.session_state.discount_percent, format="%.2f")
with col4:
    st.session_state.suggested_profit = st.number_input("🔥 Suggested Profit %", value=st.session_state.suggested_profit, format="%.2f")

if product_name:
    row = df_data[df_data.iloc[:, 0].str.lower() == product_name.lower()]
    if not row.empty:
        price_from_data = float(row.iloc[0, 1])
        st.success(f"Price per Pound found: ${price_from_data:.2f}")

        sizes = ["1 OZ", "2 OZ", "4 OZ", "8 OZ", "1 LB", "2 LB", "4 LB", "8 LB", "1 OZ SPRAY", "2 OZ SPRAY", "10 ML", "30 ML"]
        labor_cols = list(range(2, 14))

        df_key = f"df_{product_name.replace(' ', '_')}"

        if df_key not in st.session_state:
            rows = []
            for i, size in enumerate(sizes):
                labor = float(row.iloc[0, labor_cols[i]]) if i < len(labor_cols) else 0.0
                shipping_key = f"shipping_{product_name}_{size}"
                if shipping_key not in st.session_state:
                    st.session_state[shipping_key] = 0.0
                shipping = float(st.session_state[shipping_key])

                search_key = f"search_{product_name}_{size}"
                if search_key not in st.session_state:
                    st.session_state[search_key] = 20.0
                search_percent = float(st.session_state[search_key])

                price = float(price_from_data)
                discount = price * st.session_state.discount_percent / 100
                tax = price * st.session_state.tax_percent / 100
                price_plus_tax = price + tax
                fee = price * (4.2 * (100 + st.session_state.tax_percent) / 100) / 100
                profit = price - shipping - labor - fee - discount
                total_profit = profit / labor if labor > 0 else 0
                suggested_price = round(
                    (price + (price * search_percent / 100) + shipping) /
                    (1 - ((st.session_state.discount_percent + 4.2 * (100 + st.session_state.tax_percent) / 100) / 100)),
                    2
                )
                price_with_discount = price - discount if discount > 0 else "A&D"

                rows.append([
                    size,
                    round(float(labor), 2),
                    round(float(shipping), 2),
                    round(float(price), 2),
                    round(float(price_with_discount), 2) if isinstance(price_with_discount, (float, int)) else "A&D",
                    round(float(tax), 2),
                    round(float(price_plus_tax), 2),
                    round(float(fee), 2),
                    round(float(discount), 2),
                    round(float(profit), 2),
                    round(float(total_profit), 2),
                    round(float(search_percent / 100), 4),
                    round(float(suggested_price), 2)
                ])

            columns = [
                "Size", "Labor to Make", "Shipping", "Price", "Price with Discount", "Tax",
                "Price+Tax", "Fee Website", "Discount", "Profit", "Total Profit",
                "Search %", "Suggested Price"
            ]
            st.session_state[df_key] = pd.DataFrame(rows, columns=columns)

        edited_df = st.data_editor(
            st.session_state[df_key],
            column_config={
                "Shipping": st.column_config.NumberColumn("Shipping", format="$%.2f"),
                "Price": st.column_config.NumberColumn("Price", format="$%.2f"),
            },
            disabled=["Size", "Labor to Make", "Price with Discount", "Tax", "Price+Tax", "Fee Website",
                      "Discount", "Profit", "Total Profit", "Search %", "Suggested Price"],
            use_container_width=True,
            key="shipping_editor"
        )

        # Guardar valores actualizados manualmente en session_state
        for i, size in enumerate(sizes):
            st.session_state[f"shipping_{product_name}_{size}"] = float(edited_df.loc[i, "Shipping"])

        st.session_state[df_key] = edited_df

        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            if st.button("📥 PRICE"):
                edited_df["Price"] = edited_df["Suggested Price"]
                st.session_state[df_key] = edited_df
                st.success("Suggested Price copied to Price ✅")
        with col_btn2:
            if st.button("🚀 SEND WEB"):
                st.info("Feature not yet implemented")
    else:
        st.error("❌ Product not found in DATA.")