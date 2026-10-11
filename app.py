

import streamlit as st
import time
from datetime import datetime, timezone
from supabase import create_client

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
h1, h2, h3, p {
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
    margin: auto !important;
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


# ---------- SUPABASE ----------
@st.cache_resource
def get_supabase():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )

try:
    db = get_supabase()
    db_error = None
except Exception as e:
    db = None
    db_error = str(e)


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
    "loaded_player": "",
    "last_save": 0.0,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------- DATABASE FUNCTIONS ----------
def load_player(name):
    if db is None or not name:
        return

    try:
        result = (
            db.table("leaderboard")
            .select("coins")
            .eq("player_name", name)
            .limit(1)
            .execute()
        )

        if result.data:
            saved_coins = result.data[0]["coins"]
            st.session_state.coins = max(
                st.session_state.coins,
                float(saved_coins)
            )

        st.session_state.loaded_player = name

    except Exception as e:
        st.session_state.db_message = (
            f"Não foi possível carregar o jogador: {e}"
        )


def save_score():
    if db is None:
        return

    name = st.session_state.player_name.strip()
    if not name:
        return

    try:
        db.table("leaderboard").upsert(
            {
                "player_name": name,
                "coins": int(st.session_state.coins),
                "updated_at": datetime.now(
                    timezone.utc
                ).isoformat(),
            },
            on_conflict="player_name"
        ).execute()

        st.session_state.last_save = time.time()
        st.session_state.db_message = "Pontuação sincronizada!"

    except Exception as e:
        st.session_state.db_message = (
            f"Erro ao guardar pontuação: {e}"
        )


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

    new_name = st.text_input(
        "Nome do jogador",
        value=st.session_state.player_name,
        max_chars=20
    ).strip()

    if new_name:
        st.session_state.player_name = new_name

    if (
        st.session_state.player_name
        and st.session_state.loaded_player
        != st.session_state.player_name
    ):
        load_player(st.session_state.player_name)

    st.metric("Saldo", f"{st.session_state.coins:,.1f} 🪙")

    click_value = (
        st.session_state.click_power
        * st.session_state.click_multiplier
        * (1 + 5 * st.session_state.super_level)
    )

    st.metric("Ganhos por clique", f"{click_value} 🪙")
    st.metric("Ganhos automáticos", f"{st.session_state.cps} CPS")

    if db is None:
        st.warning("Base de dados não ligada. Verifica os Secrets.")


# ---------- UPGRADE FUNCTIONS ----------
def buy_upgrade(cost_key, multiplier, apply_upgrade):
    price = st.session_state[cost_key]

    if st.session_state.coins < price:
        st.warning("Ainda não tens moedas suficientes!")
        return

    st.session_state.coins -= price
    apply_upgrade()
    st.session_state[cost_key] = int(price * multiplier)

    save_score()
    st.toast("Melhoria comprada! 🚀")


def buy_normal():
    buy_upgrade(
        "normal_cost",
        1.6,
        lambda: setattr(
            st.session_state,
            "click_power",
            st.session_state.click_power + 1
        )
    )


def buy_fast():
    buy_upgrade(
        "fast_cost",
        1.8,
        lambda: setattr(
            st.session_state,
            "click_multiplier",
            st.session_state.click_multiplier + 1
        )
    )


def buy_super():
    buy_upgrade(
        "super_cost",
        2.0,
        lambda: setattr(
            st.session_state,
            "super_level",
            st.session_state.super_level + 1
        )
    )


def buy_cps():
    buy_upgrade(
        "cps_cost",
        1.7,
        lambda: setattr(
            st.session_state,
            "cps",
            st.session_state.cps + 1
        )
    )


# ---------- MAIN GAME ----------
@st.fragment(run_every=1)
def show_page():
    now = time.time()
    elapsed = min(now - st.session_state.last_time, 10)

    st.session_state.coins += st.session_state.cps * elapsed
    st.session_state.last_time = now

    click_value = (
        st.session_state.click_power
        * st.session_state.click_multiplier
        * (1 + 5 * st.session_state.super_level)
    )

    # Guardar periodicamente os ganhos automáticos.
    if now - st.session_state.last_save >= 10:
        save_score()

    if page == "🎮 Jogar":
        st.title("🪙 COIN RUSH")
        st.caption("A tua jornada para te tornares o maior colecionador!")

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
                    save_score()

            st.markdown(
                "<p class='small-note'>"
                "Clica na moeda para ganhar moedas!</p>",
                unsafe_allow_html=True
            )

        st.divider()
        a, b, c = st.columns(3)
        a.metric("👆 Poder base", st.session_state.click_power)
        b.metric("⚡ Multiplicador", f"x{st.session_state.click_multiplier}")
        c.metric("🤖 CPS", st.session_state.cps)

    elif page == "🛒 Melhorias":
        st.title("🛒 Loja de Melhorias")
        st.caption("Investe as tuas moedas para ganhares cada vez mais.")
        st.divider()

        upgrades = [
            (
                "👆 Click Normal",
                "Aumenta em +1 o poder base de cada clique.",
                "Nível",
                "click_power",
                "normal_cost",
                buy_normal,
            ),
            (
                "⚡ Click Rápido",
                "Aumenta o multiplicador dos teus cliques.",
                "Multiplicador",
                "click_multiplier",
                "fast_cost",
                buy_fast,
            ),
            (
                "🔥 Super Click",
                "Multiplica ainda mais o poder total do clique.",
                "Nível",
                "super_level",
                "super_cost",
                buy_super,
            ),
            (
                "🤖 Auto Clicker",
                "Ganhas +1 moeda automaticamente por segundo.",
                "CPS atual",
                "cps",
                "cps_cost",
                buy_cps,
            ),
        ]

        for title, description, label, level_key, cost_key, callback in upgrades:
            with st.container(border=True):
                left, middle, right = st.columns([3, 1.5, 1.5])

                with left:
                    st.markdown(f"**{title}**")
                    st.caption(description)
                    st.write(
                        f"{label}: {st.session_state[level_key]}"
                    )

                with middle:
                    st.caption("Preço")
                    st.markdown(
                        f"**{st.session_state[cost_key]:,} 🪙**"
                    )

                with right:
                    st.write("")
                    st.button(
                        "Comprar",
                        key=f"buy_{cost_key}",
                        use_container_width=True,
                        on_click=callback
                    )

        st.info("Os preços aumentam a cada compra.")

    elif page == "🏆 Leaderboard":
        st.title("🏆 Leaderboard Global")
        st.caption("Classificação guardada na base de dados.")

        if db is None:
            st.error(
                "Não foi possível ligar ao Supabase. "
                "Verifica os Secrets do Streamlit."
            )
        else:
            try:
                result = (
                    db.table("leaderboard")
                    .select("player_name, coins, updated_at")
                    .order("coins", desc=True)
                    .limit(50)
                    .execute()
                )

                if result.data:
                    for rank, player in enumerate(result.data, start=1):
                        with st.container(border=True):
                            col1, col2, col3 = st.columns([1, 3, 2])

                            with col1:
                                st.subheader(f"#{rank}")

                            with col2:
                                st.write(f"**{player['player_name']}**")

                            with col3:
                                st.write(f"{player['coins']:,} 🪙")
                else:
                    st.info(
                        "Ainda não existem pontuações. "
                        "Joga para seres o primeiro!"
                    )

            except Exception as e:
                st.error(f"Erro ao carregar o leaderboard: {e}")

            st.caption(
                "As pontuações são partilhadas, mas ainda não "
                "estão protegidas contra falsificação."
            )


show_page()

st.divider()
st.caption("Coin Rush • Continua a evoluir! 🪙")
