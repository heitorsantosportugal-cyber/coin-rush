
import streamlit as st

st.set_page_config(
    page_title="Coin Rush",
    page_icon="🪙",
    layout="wide",
    initial_sidebar_state="auto"
)

import time
from datetime import datetime, timezone
from supabase import create_client

st.markdown("""
<style>
/* Adaptar o jogo a ecrãs pequenos */
@media (max-width: 768px) {
    .block-container {
        padding: 1rem 0.7rem 3rem 0.7rem;
    }

    h1 {
        font-size: 1.8rem !important;
    }

    h2 {
        font-size: 1.4rem !important;
    }

    div.stButton > button {
        width: 100%;
        min-height: 48px;
        font-size: 1rem;
    }

    [data-testid="stSidebar"] {
        min-width: 0;
    }
}
</style>
""", unsafe_allow_html=True)

# ---------- CONFIG ----------
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
div.st-key-coin_button button {
    width: 190px !important;
    height: 190px !important;
    border-radius: 50% !important;
    background: radial-gradient(
        circle at 35% 25%,
        #fff7bd, #facc15 48%, #b77908 90%
    ) !important;
    border: 5px solid #ffe878 !important;
    box-shadow: 0 0 28px #eab30855,
                inset 0 0 12px #fff6bd !important;
    font-size: 85px !important;
}
</style>
""", unsafe_allow_html=True)

# ---------- SUPABASE ----------
@st.cache_resource
def get_db():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception:
        return None

db = get_db()

# Estado da conta do jogador
if "user" not in st.session_state:
    st.session_state.user = None

if "auth_message" not in st.session_state:
    st.session_state.auth_message = ""

# ---------- STATE ----------
defaults = {
    "coins": 0.0,
    "click_power": 1,
    "click_multiplier": 1,
    "super_level": 0,
    "cps": 0,
    "factory_level": 0,
    "rebirths": 0,
    "total_clicks": 0,
    "total_earned": 0.0,
    "upgrades_bought": 0,
    "achievements": [],
    "god_mode_unlocked": False,
    "player_name": "Player",
    "loaded_player": "",
    "last_save": 0.0,
    "last_tick": time.time(),
    "db_message": "",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---------- GAME CALCULATIONS ----------
def rebirth_multiplier():
    return 2 ** st.session_state.rebirths

def click_value():
    return (
        st.session_state.click_power
        * st.session_state.click_multiplier
        * (1 + 5 * st.session_state.super_level)
        * rebirth_multiplier()
    )

def total_cps():
    return (
        st.session_state.cps
        + st.session_state.factory_level * 5
    ) * rebirth_multiplier()

# ---------- DATABASE ----------
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
            st.session_state.coins = max(
                st.session_state.coins,
                float(result.data[0]["coins"])
            )

        st.session_state.loaded_player = name

    except Exception as e:
        st.session_state.db_message = (
            f"Erro ao carregar jogador: {e}"
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
        st.session_state.db_message = (
            "Pontuação sincronizada!"
        )

    except Exception as e:
        st.session_state.db_message = (
            f"Erro ao guardar pontuação: {e}"
        )

# ---------- ACHIEVEMENTS ----------
ACHIEVEMENTS = [
    {
        "id": "first_click",
        "name": "Primeiro Clique",
        "description": "Clica na moeda pela primeira vez.",
        "condition": lambda: st.session_state.total_clicks >= 1,
        "reward": 25,
    },
    {
        "id": "click_100",
        "name": "Clicador",
        "description": "Faz 100 cliques.",
        "condition": lambda: st.session_state.total_clicks >= 100,
        "reward": 250,
    },
    {
        "id": "coins_1000",
        "name": "Pequena Fortuna",
        "description": "Acumula 1.000 moedas.",
        "condition": lambda: st.session_state.total_earned >= 1000,
        "reward": 500,
    },
    {
        "id": "upgrade_10",
        "name": "Investidor",
        "description": "Compra 10 melhorias.",
        "condition": lambda: st.session_state.upgrades_bought >= 10,
        "reward": 1000,
    },
    {
        "id": "first_rebirth",
        "name": "Renascimento",
        "description": "Faz o primeiro Rebirth.",
        "condition": lambda: st.session_state.rebirths >= 1,
        "reward": 2500,
    },
]

def check_achievements():
    for achievement in ACHIEVEMENTS:
        if achievement["id"] in st.session_state.achievements:
            continue

        if achievement["condition"]():
            st.session_state.achievements.append(
                achievement["id"]
            )
            st.session_state.coins += achievement["reward"]
            st.session_state.total_earned += achievement["reward"]
            st.toast(
                f"🏆 Conquista: {achievement['name']}! "
                f"+{achievement['reward']} moedas"
            )

# ---------- SIDEBAR ----------
st.sidebar.title("🪙 Coin Rush")

new_name = st.sidebar.text_input(
    "Nome do jogador",
    value=st.session_state.player_name,
    max_chars=20
).strip()

if new_name and new_name != st.session_state.player_name:
    st.session_state.player_name = new_name
    st.session_state.loaded_player = ""
    load_player(new_name)

if (
    st.session_state.player_name
    and not st.session_state.loaded_player
):
    load_player(st.session_state.player_name)

# Sistema de contas
st.sidebar.divider()
st.sidebar.subheader("🔐 Conta Coin Rush")

auth_email = st.sidebar.text_input(
    "Email",
    key="auth_email"
)

auth_password = st.sidebar.text_input(
    "Palavra-passe",
    type="password",
    key="auth_password"
)


if st.sidebar.button("📝 Criar conta"):
    if db is None:
        st.session_state.auth_message = "Erro: base de dados indisponível."
    elif not auth_email or not auth_password:
        st.session_state.auth_message = "Preenche o email e a palavra-passe."
    else:
        try:
            result = db.auth.sign_up({
                "email": auth_email.strip(),
                "password": auth_password
            })

            if result.user:
                st.session_state.auth_message = (
                    "Registo enviado! Verifica o teu email para confirmar a conta."
                )
            else:
                st.session_state.auth_message = (
                    "Não foi possível concluir o registo. Tenta novamente."
                )
        except Exception:
            st.session_state.auth_message = (
                "Erro no registo. Confirma os dados e tenta novamente."
            )


if st.sidebar.button("🔑 Iniciar sessão"):
    if db is None:
        st.session_state.auth_message = "Erro: base de dados indisponível."
    elif not auth_email or not auth_password:
        st.session_state.auth_message = "Preenche o email e a palavra-passe."
    else:
        try:
            result = db.auth.sign_in_with_password({
                "email": auth_email.strip(),
                "password": auth_password
            })

            if result.user and result.session:
                st.session_state.user = {
                    "id": result.user.id,
                    "email": result.user.email
                }
                st.session_state.auth_message = (
                    "Sessão iniciada! Bem-vindo ao Coin Rush."
                )
            else:
                st.session_state.auth_message = (
                    "Não foi possível iniciar sessão."
                )
        except Exception:
            st.session_state.auth_message = (
                "Login falhou. Confirma o email, a palavra-passe "
                "e se já confirmaste o email."
            )


if st.session_state.auth_message:
    st.sidebar.info(st.session_state.auth_message)

page = st.sidebar.radio(
    "Navegação",
    [
        "Jogar",
        "Melhorias",
        "Fábrica",
        "Rebirth",
        "Conquistas",
        "Leaderboard",
        "God Mode",
        "Enviar Moedas",

    ]
)

st.sidebar.divider()
st.sidebar.metric(
    "Saldo",
    f"{st.session_state.coins:,.1f} 🪙"
)
st.sidebar.metric(
    "Por clique",
    f"{click_value():,.1f} 🪙"
)
st.sidebar.metric(
    "Por segundo",
    f"{total_cps():,.1f} CPS"
)
st.sidebar.metric(
    "Rebirths",
    str(st.session_state.rebirths)
)

if db is None:
    st.sidebar.warning(
        "Base de dados desligada. Verifica os Secrets."
    )
elif st.session_state.db_message:
    st.sidebar.caption(st.session_state.db_message)

# ---------- GAME PAGE ----------
st.title("🪙 Coin Rush")
st.caption("Clica, melhora, constrói a tua fábrica e evolui!")

@st.fragment(run_every=1)
def game_area():
    now = time.time()
    elapsed = min(now - st.session_state.last_tick, 5)
    st.session_state.last_tick = now

    passive_gain = total_cps() * elapsed
    if passive_gain > 0:
        st.session_state.coins += passive_gain
        st.session_state.total_earned += passive_gain

    
col1, col2, col3 = st.columns(3, gap="small")

with col1:
    st.metric("Saldo", f"{st.session_state.coins:,.1f} 🪙")

with col2:
    st.metric("Por clique", f"{click_value():,.1f} 🪙")

with col3:
    st.metric("Por segundo", f"{total_cps():,.1f} CPS")

    st.write("")
    left, center, right = st.columns([1, 2, 1])

    with center:
        st.markdown(
            "<h2 style='text-align:center'>Clica na moeda!</h2>",
            unsafe_allow_html=True
        )

        if st.button(
            "🪙",
            key="coin_button",
            use_container_width=True
        ):
            gain = click_value()
            st.session_state.coins += gain
            st.session_state.total_earned += gain
            st.session_state.total_clicks += 1
            check_achievements()
            save_score()

        st.caption(
            f"Total de cliques: {st.session_state.total_clicks:,}"
        )

    if time.time() - st.session_state.last_save >= 10:
        save_score()

if page == "Jogar":
    game_area()

# ---------- UPGRADES ----------
elif page == "Melhorias":
    st.header("🛒 Loja de Melhorias")
    st.write("Investe as tuas moedas para ganhares mais.")

    upgrades = [
        {
            "name": "Click Normal",
            "description": "+1 poder de clique",
            "cost": 50 * (st.session_state.click_power ** 2),
            "key": "normal",
        },
        {
            "name": "Click Rápido",
            "description": "+1 multiplicador de clique",
            "cost": 150 * (st.session_state.click_multiplier ** 2),
            "key": "fast",
        },
        {
            "name": "Super Click",
            "description": "Aumenta muito os ganhos por clique",
            "cost": 500 * ((st.session_state.super_level + 1) ** 2),
            "key": "super",
        },
        {
            "name": "Auto Clicker",
            "description": "+1 moeda automática por segundo",
            "cost": 300 * ((st.session_state.cps + 1) ** 2),
            "key": "auto",
        },
    ]

    for upgrade in upgrades:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.subheader(upgrade["name"])
                st.write(upgrade["description"])
                st.caption(
                    f"Custo: {upgrade['cost']:,} moedas"
                )

            with col2:
                if st.button(
                    "Comprar",
                    key=f"buy_{upgrade['key']}",
                    use_container_width=True
                ):
                    if st.session_state.coins >= upgrade["cost"]:
                        st.session_state.coins -= upgrade["cost"]

                        if upgrade["key"] == "normal":
                            st.session_state.click_power += 1
                        elif upgrade["key"] == "fast":
                            st.session_state.click_multiplier += 1
                        elif upgrade["key"] == "super":
                            st.session_state.super_level += 1
                        elif upgrade["key"] == "auto":
                            st.session_state.cps += 1

                        st.session_state.upgrades_bought += 1
                        check_achievements()
                        save_score()
                        st.success("Melhoria comprada!")
                        st.rerun()
                    else:
                        st.warning("Ainda não tens moedas suficientes.")

# ---------- FACTORY ----------
elif page == "Fábrica":
    st.header("🏭 Fábrica de Moedas")
    st.write(
        "Cada nível da fábrica produz 5 moedas por segundo, "
        "antes do multiplicador de Rebirth."
    )

    st.metric(
        "Nível da fábrica",
        st.session_state.factory_level
    )
    st.metric(
        "Produção da fábrica",
        f"{st.session_state.factory_level * 5 * rebirth_multiplier():,.1f} CPS"
    )

    factory_cost = 1000 * ((st.session_state.factory_level + 1) ** 2)

    st.subheader("Comprar uma fábrica")
    st.write(f"Custo do próximo nível: **{factory_cost:,} moedas**")

    if st.button("🏭 Melhorar fábrica", use_container_width=True):
        if st.session_state.coins >= factory_cost:
            st.session_state.coins -= factory_cost
            st.session_state.factory_level += 1
            st.session_state.upgrades_bought += 1
            check_achievements()
            save_score()
            st.success("A fábrica foi melhorada!")
            st.rerun()
        else:
            st.warning("Ainda não tens moedas suficientes.")

# ---------- REBIRTH ----------
elif page == "Rebirth":
    st.header("♻️ Rebirth")
    st.write(
        "Recomeça a tua aventura em troca de um multiplicador "
        "permanente de ganhos."
    )

    required_coins = 100_000 * (st.session_state.rebirths + 1)
    next_multiplier = 2 ** (st.session_state.rebirths + 1)

    st.metric("Rebirths feitos", st.session_state.rebirths)
    st.metric("Multiplicador atual", f"x{rebirth_multiplier()}")
    st.metric("Próximo multiplicador", f"x{next_multiplier}")
    st.metric("Moedas necessárias", f"{required_coins:,} 🪙")

    st.warning(
        "O Rebirth reinicia o saldo, os cliques melhorados, "
        "o Auto Clicker e a fábrica. O número de Rebirths "
        "e o multiplicador permanente ficam contigo."
    )

    if st.button("♻️ Fazer Rebirth", use_container_width=True):
        if st.session_state.coins >= required_coins:
            st.session_state.rebirths += 1
            st.session_state.coins = 0.0
            st.session_state.click_power = 1
            st.session_state.click_multiplier = 1
            st.session_state.super_level = 0
            st.session_state.cps = 0
            st.session_state.factory_level = 0
            st.session_state.last_tick = time.time()
            save_score()
            st.success("Rebirth concluído! O teu multiplicador aumentou.")
            st.rerun()
        else:
            st.warning(
                f"Precisas de mais "
                f"{required_coins - st.session_state.coins:,.1f} moedas."
            )

# ---------- ACHIEVEMENTS PAGE ----------
elif page == "Conquistas":
    st.header("🏆 Conquistas e Missões")
    st.write(
        "Completa objetivos para desbloqueares recompensas."
    )

    completed = len(st.session_state.achievements)
    st.progress(completed / len(ACHIEVEMENTS))
    st.write(f"Conquistas desbloqueadas: {completed}/{len(ACHIEVEMENTS)}")

    for achievement in ACHIEVEMENTS:
        is_done = achievement["id"] in st.session_state.achievements

        with st.container(border=True):
            col1, col2 = st.columns([4, 1])

            with col1:
                st.subheader(
                    ("✅ " if is_done else "🔒 ")
                    + achievement["name"]
                )
                st.write(achievement["description"])
                st.caption(
                    f"Recompensa: {achievement['reward']:,} moedas"
                )

            with col2:
                st.write("Concluída" if is_done else "Por fazer")

    st.divider()
    st.subheader("📋 Missões atuais")

    missions = [
        ("Fazer 10 cliques", st.session_state.total_clicks, 10),
        ("Fazer 100 cliques", st.session_state.total_clicks, 100),
        ("Comprar 5 melhorias", st.session_state.upgrades_bought, 5),
        ("Chegar a 10 CPS", total_cps(), 10),
    ]

    for label, progress, target in missions:
        st.write(f"**{label}** — {min(progress, target):,.0f}/{target}")
        st.progress(min(float(progress) / target, 1.0))

# ---------- LEADERBOARD ----------
elif page == "Leaderboard":
    st.header("🏆 Leaderboard Global")
    st.write("As pontuações são carregadas da base de dados partilhada.")

    if db is None:
        st.error("Não foi possível ligar ao Supabase. Verifica os Secrets.")
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
                for index, player in enumerate(result.data, start=1):
                    medal = (
                        "🥇" if index == 1
                        else "🥈" if index == 2
                        else "🥉" if index == 3
                        else f"**{index}.**"
                    )

                    col1, col2 = st.columns([3, 1])
                    col1.write(f"{medal} {player['player_name']}")
                    col2.write(f"{player['coins']:,} 🪙")
            else:
                st.info("Ainda não existem pontuações guardadas.")

        except Exception as e:
            st.error(f"Erro ao carregar o leaderboard: {e}")

    st.caption(
        "Nota: esta versão de teste ainda não tem autenticação "
        "nem proteção completa contra pontuações falsas."
    )


elif page == "God Mode":
    st.header("👑 God Mode")
    st.write("Área de administrador do Coin Rush.")

    if not st.session_state.god_mode_unlocked:
        password = st.text_input(
            "Código secreto de administrador",
            type="password",
        )

        if st.button("🔓 Desbloquear God Mode"):
            if password and password == st.secrets.get(
                "GOD_MODE_PASSWORD", ""
            ):
                st.session_state.god_mode_unlocked = True
                st.success("God Mode desbloqueado!")
                st.rerun()
            else:
                st.error("Código incorreto.")

    else:
        st.success("👑 Acesso de administrador ativo!")

        st.subheader("💰 Gerador de moedas")

        

        quantidade_texto = st.text_input(
            "Quantas moedas queres adicionar?",
            value="5000000000000",
            help="Escreve a quantidade de moedas que queres receber."
        )

        confirmar = st.checkbox(
            "Confirmo que quero adicionar esta quantidade."
        )

        if st.button("💸 ADICIONAR MOEDAS", type="primary"):
            try:
                quantidade = int(quantidade_texto.strip())

                if quantidade <= 0:
                    st.error("Introduz um número maior que zero.")
                elif not confirmar:
                    st.warning("Confirma a operação primeiro.")
                else:
                    st.session_state.coins += quantidade
                    st.session_state.total_earned += quantidade
                    save_score()
                    st.success(
                        f"Adicionadas {quantidade:,} moedas!"
                    )
                    st.rerun()

            except ValueError:
                st.error("Introduz um número inteiro válido.")


        if st.button("🔒 Bloquear God Mode"):
            st.session_state.god_mode_unlocked = False
            st.rerun()

elif page == "Enviar Moedas":
    st.header("🎁 Enviar Moedas")
    st.write("Transfere moedas para outro jogador do Coin Rush.")

    if db is None:
        st.error("Não foi possível ligar ao Supabase.")
    else:
        try:
            result = (
                db.table("leaderboard")
                .select("player_name, coins")
                .order("player_name")
                .execute()
            )

            players = [
                player["player_name"]
                for player in (result.data or [])
                if player["player_name"] != st.session_state.player_name
            ]

            if not players:
                st.info("Ainda não existem outros jogadores disponíveis.")
            else:
                recipient = st.selectbox(
                    "Escolhe o destinatário",
                    players,
                )

                amount = st.number_input(
                    "Quantidade de moedas",
                    min_value=1,
                    step=1,
                )

                st.write(
                    f"**O teu saldo atual:** "
                    f"{int(st.session_state.coins):,} 🪙"
                )

                if st.button("🎁 Enviar moedas"):
                    st.info(
                        "Formulário preparado! Falta implementar a "
                        "transferência segura na base de dados."
                    )

        except Exception as e:
            st.error(f"Erro ao carregar jogadores: {e}")

# ---------- FOOTER ----------
st.divider()
st.caption("Coin Rush • Update 2.0 • Feito com Python + Streamlit")
