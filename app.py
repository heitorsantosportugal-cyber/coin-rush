
import streamlit as st
import time

st.set_page_config(
    page_title="Coin Rush",
    page_icon="🪙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- DESIGN ----------
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top, #25204b, #0b0b18 75%);
    color: white;
}
[data-testid="stSidebar"] {
    background: #151529;
    border-right: 1px solid #39345c;
}
h1, h2, h3, p, label {
    color: white;
}
div.stButton > button {
    border-radius: 10px;
    border: 1px solid #49436b;
    background: #201e3a;
    color: white;
    transition: 0.15s;
}
div.stButton > button:hover {
    border-color: #facc15;
    color: #facc15;
}
div.st-key-coin button {
    width: 190px !important;
    min-width: 190px !important;
    max-width: 190px !important;
    height: 190px !important;
    min-height: 190px !important;
    border-radius: 50% !important;
    padding: 0 !important;
    margin: 0 auto !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    background: radial-gradient(circle at 35% 25%,
        #fff7bd, #facc15 48%, #b77908 90%) !important;
    border: 5px solid #ffe878 !important;
    box-shadow: 0 0 28px #eab30855,
                inset 0 0 12px #fff6bd !important;
    font-size: 95px !important;
    line-height: 1 !important;
}
div.st-key-coin button:hover {
    transform: scale(1.04);
    color: white !important;
}
div.st-key-coin button:active {
    transform: scale(0.94);
}
.small-note {
    color: #b8b8d5;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ---------- GAME DATA ----------
defaults = {
    "coins": 0.0,
    "click_power": 1,
    "click_multiplier": 1,
    "super_level": 0,
    "cps": 0,
    "normal_cost": 25,
    "fast_cost": 100,
    "super_cost": 500,
    "cps_cost": 50,
    "last_time": time.time(),
    "player_name": "Jogador",
    "total_clicks": 0,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---------- SIDEBAR ----------
with st.sidebar:
    st.title("🪙 COIN RUSH")
    st.caption("Clica. Evolui. Domina.")

    page = st.radio(
        "MENU",
        ["🎮 Jogar", "🛒 Melhorias", "🏆 Leaderboard"],
        label_visibility="collapsed"
    )

    st.divider()
    st.metric("Saldo", f"{st.session_state.coins:,.1f} 🪙")
    st.metric("Ganhos por clique",
              f"{st.session_state.click_power * st.session_state.click_multiplier} 🪙")
    st.metric("Ganhos automáticos", f"{st.session_state.cps} CPS")

    st.divider()
    st.session_state.player_name = st.text_input(
        "Nome do jogador",
        value=st.session_state.player_name,
        max_chars=20
    ).strip() or "Jogador"

# ---------- UPGRADE HELPERS ----------
def buy_upgrade(cost_key, price_multiplier, apply_upgrade):
    cost = st.session_state[cost_key]

    if st.session_state.coins >= cost:
        st.session_state.coins -= cost
        apply_upgrade()
        st.session_state[cost_key] = int(cost * price_multiplier)
        st.toast("Melhoria comprada! 🚀")
    else:
        st.warning("Ainda não tens moedas suficientes!")

def buy_normal():
    buy_upgrade(
        "normal_cost", 1.6,
        lambda: setattr(
            st.session_state, "click_power",
            st.session_state.click_power + 1
        )
    )

def buy_fast():
    buy_upgrade(
        "fast_cost", 1.8,
        lambda: setattr(
            st.session_state, "click_multiplier",
            st.session_state.click_multiplier + 1
        )
    )

def buy_super():
    buy_upgrade(
        "super_cost", 2.0,
        lambda: setattr(
            st.session_state, "super_level",
            st.session_state.super_level + 1
        )
    )
    # O Super Click também aumenta o poder do clique.
    # O efeito é aplicado na função de compra abaixo.

def buy_cps():
    buy_upgrade(
        "cps_cost", 1.7,
        lambda: setattr(
            st.session_state, "cps",
            st.session_state.cps + 1
        )
    )

# ---------- MAIN CONTENT ----------
@st.fragment(run_every=1)
def show_page():
    # Atualizar os ganhos automáticos com o tempo.
    now = time.time()
    elapsed = min(now - st.session_state.last_time, 10)
    st.session_state.coins += st.session_state.cps * elapsed
    st.session_state.last_time = now

    # Poder final do clique.
    click_value = (
        st.session_state.click_power
        * st.session_state.click_multiplier
        * (1 + 5 * st.session_state.super_level)
    )

    if page == "🎮 Jogar":
        st.title("🪙 COIN RUSH")
        st.caption("A tua jornada para te tornares o maior colecionador!")

        st.write("")
        st.write("")

        left, center, right = st.columns([1, 2, 1])

        with center:
            st.markdown(
                f"<h1 style='text-align:center;color:#facc15;"
                f"font-size:38px'>{st.session_state.coins:,.1f} 🪙</h1>",
                unsafe_allow_html=True
            )
            st.markdown(
                f"<p style='text-align:center'>"
                f"+{click_value} moedas por clique</p>",
                unsafe_allow_html=True
            )

            _, coin_col, _ = st.columns([0.5, 2, 0.5])
            with coin_col:
                if st.button("🪙", key="coin"):
                    st.session_state.coins += click_value
                    st.session_state.total_clicks += 1

            st.markdown(
                "<p class='small-note'>Clica na moeda para ganhar moedas!</p>",
                unsafe_allow_html=True
            )

        st.write("")
        st.divider()

        a, b, c = st.columns(3)
        a.metric("👆 Poder base", st.session_state.click_power)
        b.metric("⚡ Multiplicador", f"x{st.session_state.click_multiplier}")
        c.metric("🤖 Moedas por segundo", st.session_state.cps)

    elif page == "🛒 Melhorias":
        st.title("🛒 Loja de Melhorias")
        st.caption("Compra melhorias para ganhares moedas cada vez mais depressa.")
        st.divider()

        # Click Normal
        with st.container(border=True):
            left, middle, right = st.columns([3, 2, 2])
            with left:
                st.subheader("👆 Click Normal")
                st.caption("Aumenta em +1 o poder base de cada clique.")
                st.write(f"Nível atual: {st.session_state.click_power}")
            with middle:
                st.write("Preço")
                st.markdown(f"### {st.session_state.normal_cost} 🪙")
            with right:
                st.write("")
                st.button(
                    "Comprar",
                    key="buy_normal",
                    use_container_width=True,
                    on_click=buy_normal
                )

        # Click Rápido
        with st.container(border=True):
            left, middle, right = st.columns([3, 2, 2])
            with left:
                st.subheader("⚡ Click Rápido")
                st.caption("Aumenta o multiplicador dos teus cliques.")
                st.write(f"Multiplicador atual: x{st.session_state.click_multiplier}")
            with middle:
                st.write("Preço")
                st.markdown(f"### {st.session_state.fast_cost} 🪙")
            with right:
                st.write("")
                st.button(
                    "Comprar",
                    key="buy_fast",
                    use_container_width=True,
                    on_click=buy_fast
                )

        # Super Click
        with st.container(border=True):
            left, middle, right = st.columns([3, 2, 2])
            with left:
                st.subheader("🔥 Super Click")
                st.caption("Multiplica ainda mais o poder total do clique.")
                st.write(f"Nível atual: {st.session_state.super_level}")
            with middle:
                st.write("Preço")
                st.markdown(f"### {st.session_state.super_cost} 🪙")
            with right:
                st.write("")
                st.button(
                    "Comprar",
                    key="buy_super",
                    use_container_width=True,
                    on_click=buy_super
                )

        # Auto Clicker
        with st.container(border=True):
            left, middle, right = st.columns([3, 2, 2])
            with left:
                st.subheader("🤖 Auto Clicker")
                st.caption("Ganhas +1 moeda automaticamente por segundo.")
                st.write(f"Produção atual: {st.session_state.cps} CPS")
            with middle:
                st.write("Preço")
                st.markdown(f"### {st.session_state.cps_cost} 🪙")
            with right:
                st.write("")
                st.button(
                    "Comprar",
                    key="buy_cps",
                    use_container_width=True,
                    on_click=buy_cps
                )

        st.divider()
        st.info("Os preços aumentam cada vez que compras uma melhoria.")

    elif page == "🏆 Leaderboard":
        st.title("🏆 Leaderboard")
        st.caption("Classificação de exemplo — a tabela global será ligada a uma base de dados.")

        # Demonstração local: não é ainda uma classificação partilhada.
        demo_players = [
            {"Jogador": "CoinMaster", "Moedas": 12500},
            {"Jogador": "GoldenClick", "Moedas": 8700},
            {"Jogador": "FastFinger", "Moedas": 4200},
        ]
        demo_players.append({
            "Jogador": st.session_state.player_name,
            "Moedas": int(st.session_state.coins)
        })
        demo_players.sort(key=lambda player: player["Moedas"], reverse=True)

        for i, player in enumerate(demo_players, start=1):
            with st.container(border=True):
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.subheader(f"#{i}")
                with col2:
                    st.write(f"**{player['Jogador']}**")
                    st.caption(f"{player['Moedas']:,} moedas")

        st.warning(
            "Esta classificação ainda é uma demonstração. "
            "Para todos os jogadores verem a mesma tabela, "
            "vamos ligar o jogo a uma base de dados."
        )

show_page()

st.divider()
st.caption("Coin Rush • Continua a evoluir! 🪙")
