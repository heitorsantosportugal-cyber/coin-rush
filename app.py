
import streamlit as st
import time

st.set_page_config(
    page_title="Coin Rush",
    page_icon="🪙",
    layout="wide"
)

# VISUAL DO JOGO
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at center, #25204b, #0b0b18);
    color: white;
}
[data-testid="stSidebar"] {
    background: #151529;
}
h1, h2, h3, p {
    color: white;
}
div.st-key-coin button {
    width: 220px;
    height: 220px;
    border-radius: 50%;
    background: radial-gradient(circle at 35% 30%,
        #fff2a6, #facc15 45%, #b77908 85%);
    border: 8px solid #ffe878;
    box-shadow: 0 0 35px #eab30888,
                inset 0 0 15px #fff6bd;
    font-size: 100px;
    transition: transform 0.1s;
}
div.st-key-coin button:hover {
    transform: scale(1.05);
    border-color: #fff2a6;
    color: white;
}
div.st-key-coin button:active {
    transform: scale(0.94);
}
</style>
""", unsafe_allow_html=True)

# DADOS DO JOGO
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

# CALCULAR GANHOS AUTOMÁTICOS
def update_coins():
    now = time.time()
    elapsed = min(now - st.session_state.last_time, 60)
    st.session_state.coins += st.session_state.cps * elapsed
    st.session_state.last_time = now

update_coins()

# LOJA
with st.sidebar:
    st.title("🛒 COIN SHOP")
    st.metric("Saldo", f"{st.session_state.coins:.1f} 🪙")
    st.divider()

    st.subheader("👆 Poder do clique")
    st.write(f"+{st.session_state.click_power} moedas por clique")
    st.write(f"Preço: {st.session_state.click_cost} 🪙")

    if st.button("Comprar melhoria de clique",
                 use_container_width=True):
        if st.session_state.coins >= st.session_state.click_cost:
            st.session_state.coins -= st.session_state.click_cost
            st.session_state.click_power += 1
            st.session_state.click_cost = int(
                st.session_state.click_cost * 1.6
            )
            st.rerun()
        else:
            st.warning("Precisas de mais moedas!")

    st.divider()
    st.subheader("⚡ Auto-clicker")
    st.write(f"{st.session_state.cps} moedas por segundo")
    st.write(f"Preço: {st.session_state.cps_cost} 🪙")

    if st.button("Comprar +1 CPS", use_container_width=True):
        if st.session_state.coins >= st.session_state.cps_cost:
            st.session_state.coins -= st.session_state.cps_cost
            st.session_state.cps += 1
            st.session_state.cps_cost = int(
                st.session_state.cps_cost * 1.7
            )
            st.rerun()
        else:
            st.warning("Precisas de mais moedas!")

    st.divider()
    if st.button("🔄 Reiniciar jogo", use_container_width=True):
        for key, value in defaults.items():
            st.session_state[key] = value
        st.rerun()

# JOGO CENTRAL
st.title("🪙 COIN RUSH")
st.caption("Clica na moeda. Acumula riqueza. Evolui!")

left, center, right = st.columns([1, 2, 1])

with center:
    st.markdown(
        f"<h1 style='text-align:center;color:#facc15'>"
        f"🪙 {st.session_state.coins:.1f}</h1>",
        unsafe_allow_html=True
    )

    st.markdown(
        f"<p style='text-align:center'>"
        f"+{st.session_state.click_power} moedas por clique"
        f"</p>",
        unsafe_allow_html=True
    )

    st.button("🪙", key="coin", use_container_width=True,
              on_click=lambda: setattr(
                  st.session_state,
                  "coins",
                  st.session_state.coins + st.session_state.click_power
              ))

    st.markdown(
        "<p style='text-align:center;color:#b8b8d5'>"
        "Clica diretamente na moeda para ganhar!"
        "</p>",
        unsafe_allow_html=True
    )

st.divider()

col1, col2 = st.columns(2)
col1.metric("👆 Poder do clique",
            st.session_state.click_power)
col2.metric("⚡ CPS",
            st.session_state.cps)
