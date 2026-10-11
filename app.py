
import streamlit as st
import time

st.set_page_config(
    page_title="Coin Rush",
    page_icon="🪙",
    layout="wide"
)

# ---------- ESTILO ----------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #101020, #1b1740);
    color: white;
}
h1, h2, h3, p, label {
    color: white !important;
}
div.stButton > button {
    border-radius: 12px;
    font-weight: bold;
    min-height: 45px;
}
.coin-button div.stButton > button {
    background: #facc15;
    color: #171717;
    border: none;
    font-size: 24px;
    min-height: 100px;
}
</style>
""", unsafe_allow_html=True)

# ---------- ESTADO DO JOGO ----------
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

# ---------- MOEDAS AUTOMÁTICAS ----------
now = time.time()
elapsed = min(now - st.session_state.last_time, 10)
st.session_state.coins += st.session_state.cps * elapsed
st.session_state.last_time = now

# ---------- BARRA LATERAL ----------
with st.sidebar:
    st.title("🛒 Loja")
    st.caption("Usa as tuas moedas para evoluir!")

    st.divider()
    st.subheader("👆 Poder de clique")
    st.write(f"+{st.session_state.click_power} moedas por clique")
    st.write(f"Custo: 🪙 {st.session_state.click_cost}")

    if st.button("Comprar poder de clique", use_container_width=True):
        if st.session_state.coins >= st.session_state.click_cost:
            st.session_state.coins -= st.session_state.click_cost
            st.session_state.click_power += 1
            st.session_state.click_cost = int(
                st.session_state.click_cost * 1.6
            )
            st.rerun()
        else:
            st.warning("Ainda não tens moedas suficientes!")

    st.divider()
    st.subheader("⚡ Auto-clicker")
    st.write(f"+{st.session_state.cps} moedas por segundo")
    st.write(f"Custo: 🪙 {st.session_state.cps_cost}")

    if st.button("Comprar +1 CPS", use_container_width=True):
        if st.session_state.coins >= st.session_state.cps_cost:
            st.session_state.coins -= st.session_state.cps_cost
            st.session_state.cps += 1
            st.session_state.cps_cost = int(
                st.session_state.cps_cost * 1.7
            )
            st.rerun()
        else:
            st.warning("Ainda não tens moedas suficientes!")

    st.divider()
    if st.button("🔄 Reiniciar jogo", use_container_width=True):
        for key, value in defaults.items():
            st.session_state[key] = value
        st.rerun()

# ---------- ECRÃ PRINCIPAL ----------
st.title("🪙 Coin Rush")
st.caption("Clica, acumula moedas e fica cada vez mais rico!")

st.metric("💰 Saldo", f"{st.session_state.coins:.1f} moedas")

col1, col2 = st.columns(2)
col1.metric("👆 Moedas por clique", st.session_state.click_power)
col2.metric("⚡ Moedas por segundo", st.session_state.cps)

st.write("")

st.markdown('<div class="coin-button">', unsafe_allow_html=True)
if st.button("🪙 CLICA NA MOEDA!", use_container_width=True):
    st.session_state.coins += st.session_state.click_power
    st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

st.caption("Dica: compra auto-clickers para ganhares moedas mesmo sem clicar!")
