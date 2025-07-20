import streamlit as st

st.set_page_config(page_title="Unique Agency", layout="wide")

if 'page' not in st.session_state:
    st.session_state.page = 'home'

# 🏠 Home Page
if st.session_state.page == 'home':
    st.title("🏢 Unique Agency")
    st.markdown("### Welcome! Choose an option:")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📦 Inventory Management", use_container_width=True):
            st.session_state.page = 'inventory'

    with col2:
        if st.button("📋 Price List", use_container_width=True):
            st.session_state.page = 'pricelist'

# 📦 Inventory Management Page
elif st.session_state.page == 'inventory':
    from inventory_app import run_inventory_app
    run_inventory_app()
    if st.button("🔙 Home"):
        st.session_state.page = 'home'

# 📋 Price List Page
elif st.session_state.page == 'pricelist':
    from product_catalog_app_full_multiselect import run_pricelist_app
    run_pricelist_app()
    if st.button("🔙 Home"):
        st.session_state.page = 'home'