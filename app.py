
import streamlit as st
import time

st.set_page_config(
    page_title="Coin Rush",
    page_icon="🪙",
    layout="wide"
)

# ESTILO DO JOGO
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at center, #25204b, #0b0b18);
    color: white;
}
[data-testid="stSidebar"] {
    background: #151529;
}
h1, h2, h3, p, label {
    color: white;
}
.coin-area {
    text-align: center;
    padding: 30px 0 15px 0;
}
.coin {
    font-size: 150px;
    filter: drop-shadow(0 0 25px #facc15);
}
.balance {
    text-align: center;
    font-size: 42px;
    font-weight: 800;
    color: #facc15;
}
div.stButton > button {
    border-radius: 14px;
    min-height: 48px;
    font-weight: bold;
}
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #ffe066, #f59e0b);
    color: #201300;
    border: none;
    font-size: 22px;
    min-height: 75px;
}
</style>
""", unsafe_allow_html=True)

# ESTADO INICIAL
defaults = {
    "coins": 0.0,
    "click_power": 1,
    "click_cost": 25,
    "cps": 0,
    "cps_cost": 50,
    "last_time": time.time()
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# GANHOS AUTOMÁTICOS
now = time.time()
elapsed = min(now - st.session_state.last_time, 60)
st.session_state.coins += st.session_state.cps * elapsed
st.session_state.last_time = now

# LOJA LATERAL
with st.sidebar:
    st.title("🛒 COIN SHOP")
    st.caption("Investe as tuas moedas!")

    st.divider()
    st.subheader("👆 Upgrade de clique")
    st.write(f"Atual: +{st.session_state.click_power} por clique")
    st.write(f"Preço: 🪙 {st.session_state.click_cost}")

    if st.button("Comprar poder de clique", use_container_width=True):
        if st.session_state.coins >= st.session_state.click_cost:
            st.session_state.coins -= st.session_state.click_cost
            st.session_state.click_power += 1
            st.session_state.click_cost = int(
                st.session_state.click_cost * 1.6
            )
            st.rerun()
        else:
            st.warning("Moedas insuficientes!")

    st.divider()
    st.subheader("⚡ Auto-clicker")
    st.write(f"Atual: {st.session_state.cps} CPS")
    st.write(f"Preço: 🪙 {st.session_state.cps_cost}")

    if st.button("Comprar +1 CPS", use_container_width=True):
        if st.session_state.coins >= st.session_state.cps_cost:
            st.session_state.coins -= st.session_state.cps_cost
            st.session_state.cps += 1
            st.session_state.cps_cost = int(
                st.session_state.cps_cost * 1.7
            )
            st.rerun()
        else:
            st.warning("Moedas insuficientes!")

    st.divider()
    if st.button("🔄 Reiniciar jogo", use_container_width=True):
        for key, value in defaults.items():
            st.session_state[key] = value
        st.rerun()

# ECRÃ CENTRAL
st.title("🪙 Coin Rush")
st.caption("Clica na moeda. Ganha moedas. Evolui!")

st.markdown(
    f'<div class="balance">🪙 {st.session_state.coins:.1f}</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="coin-area"><div class="coin">🪙</div></div>',
    unsafe_allow_html=True
)

st.markdown(
    f'<p style="text-align:center">+{st.session_state.click_power} moedas por clique</p>',
    unsafe_allow_html=True
)

_, center, _ = st.columns([1, 2, 1])
with center:
    if st.button(
        "🪙 CLICAR NA MOEDA",
        type="primary",
        use_container_width=True
    ):
        st.session_state.coins += st.session_state.click_power
        st.rerun()

st.write("")
left, right = st.columns(2)
left.metric("👆 Poder de clique", st.session_state.click_power)
right.metric("⚡ Moedas por segundo", st.session_state.cps)

st.caption("Dica: compra CPS para acumular moedas automaticamente.")

