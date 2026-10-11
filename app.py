
import streamlit as st

st.set_page_config(
    page_title="Coin Rush",
    page_icon="🪙",
    layout="centered"
)

st.title("🪙 Coin Rush")
st.subheader("Clica. Ganha. Evolui!")

if "coins" not in st.session_state:
    st.session_state.coins = 0

st.metric("As tuas moedas", st.session_state.coins)

if st.button("🪙 CLICA AQUI!", use_container_width=True):
    st.session_state.coins += 1
    st.rerun()

st.caption("Cada clique vale 1 moeda!")
