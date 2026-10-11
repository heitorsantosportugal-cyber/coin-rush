                else:
                    st.warning("Ainda não tens moedas suficientes.")

# ---------- FACTORY ----------
elif page == "Fábrica":
    st.header("🏭 Fábrica de Moedas")
    st.write("Cada nível produz 5 moedas por segundo, antes do multiplicador de Rebirth.")
    st.metric("Nível da fábrica", st.session_state.factory_level)
    st.metric("Produção da fábrica", f"{st.session_state.factory_level * 5 * rebirth_multiplier():,.1f} CPS")
    cost = 1000 * (st.session_state.factory_level + 1)**2
    st.write(f"Custo do próximo nível: **{cost:,} moedas**")
    if st.button("🏭 Melhorar fábrica", use_container_width=True):
        if st.session_state.coins >= cost:
            st.session_state.coins -= cost
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
    required = 100_000 * (st.session_state.rebirths + 1)
    st.metric("Rebirths feitos", st.session_state.rebirths)
    st.metric("Multiplicador atual", f"x{rebirth_multiplier()}")
    st.metric("Próximo multiplicador", f"x{2 ** (st.session_state.rebirths + 1)}")
    st.metric("Moedas necessárias", f"{required:,} 🪙")
    st.warning("O Rebirth reinicia o saldo, melhorias e fábrica. Os Rebirths ficam contigo.")
    if st.button("♻️ Fazer Rebirth", use_container_width=True):
        if st.session_state.coins >= required:
            st.session_state.rebirths += 1
            st.session_state.coins = 0.0
            st.session_state.click_power = 1
            st.session_state.click_multiplier = 1
            st.session_state.super_level = 0
            st.session_state.cps = 0
            st.session_state.factory_level = 0
            st.session_state.last_tick = time.time()
            save_score()
            st.success("Rebirth concluído!")
            st.rerun()
        else:
            st.warning(f"Precisas de mais {required - st.session_state.coins:,.1f} moedas.")

# ---------- ACHIEVEMENTS PAGE ----------
elif page == "Conquistas":
    st.header("🏆 Conquistas e Missões")
    completed = len(st.session_state.achievements)
    st.progress(completed / len(ACHIEVEMENTS))
    st.write(f"Conquistas desbloqueadas: {completed}/{len(ACHIEVEMENTS)}")
    for achievement in ACHIEVEMENTS:
        done = achievement["id"] in st.session_state.achievements
        with st.container(border=True):
            st.subheader(("✅ " if done else "🔒 ") + achievement["name"])
            st.write(achievement["description"])
            st.caption(f"Recompensa: {achievement['reward']:,} moedas")
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
    try:
        result = db.table("leaderboard").select("player_name, coins, updated_at").order("coins", desc=True).limit(50).execute()
        if result.data:
            for index, player in enumerate(result.data, start=1):
                medal = "🥇" if index == 1 else "🥈" if index == 2 else "🥉" if index == 3 else f"**{index}.**"
                c1, c2 = st.columns([3, 1])
                c1.write(f"{medal} {player['player_name']}")
                c2.write(f"{int(player['coins']):,} 🪙")
        else:
            st.info("Ainda não existem pontuações guardadas.")
    except Exception as exc:
        st.error("Não foi possível carregar o leaderboard. Confirma as políticas RLS.")
        st.caption(f"{type(exc).__name__}: {exc}")

# ---------- GOD MODE ----------
elif page == "God Mode":
    st.header("👑 God Mode")
    st.write("Área de administrador do Coin Rush.")
    if not st.session_state.god_mode_unlocked:
        password = st.text_input("Código secreto de administrador", type="password")
        if st.button("🔓 Desbloquear God Mode"):
            secret = st.secrets.get("GOD_MODE_PASSWORD", "")
            if secret and password and password == secret:
                st.session_state.god_mode_unlocked = True
                st.success("God Mode desbloqueado!")
                st.rerun()
            else:
                st.error("Código incorreto ou GOD_MODE_PASSWORD não configurado nos Secrets.")
    else:
        st.success("👑 Acesso de administrador ativo!")
        quantity_text = st.text_input("Quantas moedas queres adicionar?", value="5000000000000")
        confirm = st.checkbox("Confirmo que quero adicionar esta quantidade.")
        if st.button("💸 ADICIONAR MOEDAS", type="primary"):
            try:
                quantity = int(quantity_text.strip())
                if quantity <= 0:
                    st.error("Introduz um número maior que zero.")
                elif not confirm:
                    st.warning("Confirma a operação primeiro.")
                else:
                    st.session_state.coins += quantity
                    st.session_state.total_earned += quantity
                    save_score()
                    st.success(f"Adicionadas {quantity:,} moedas!")
                    st.rerun()
            except ValueError:
                st.error("Introduz um número inteiro válido.")
        if st.button("🔒 Bloquear God Mode"):
            st.session_state.god_mode_unlocked = False
            st.rerun()

# ---------- SEND COINS ----------
elif page == "Enviar Moedas":
    st.header("🎁 Enviar Moedas")
    st.write("A interface de transferência está preparada, mas a transferência real está desativada até ser criada uma função SQL transacional segura.")
    st.info("Não envies moedas ainda. Uma transferência segura tem de ser validada na base de dados para impedir saldo negativo e alterações falsas.")
    try:
        result = db.table("leaderboard").select("player_name").order("player_name").limit(100).execute()
        names = [row["player_name"] for row in (result.data or []) if row["player_name"] != st.session_state.player_name]
        if names:
            st.selectbox("Jogador destinatário", names)
            st.number_input("Quantidade de moedas", min_value=1, step=1)
            st.button("🎁 Enviar moedas", disabled=True, help="Será ativado quando a função SQL segura estiver instalada.")
        else:
            st.info("Ainda não existem outros jogadores.")
    except Exception:
        st.warning("Não foi possível carregar a lista de jogadores.")

st.divider()
st.caption("Coin Rush • Update 3.0 • Python + Streamlit + Supabase")
