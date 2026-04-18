import streamlit as st

user = st.session_state.get("user")

if user:
    st.sidebar.success(f"👤 {user}")

    if st.sidebar.button("Logout"):
        del st.session_state["user"]
        st.experimental_rerun()
else:
    st.sidebar.info("Not logged in")