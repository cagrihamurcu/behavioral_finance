import streamlit as st
import random
import time
import pandas as pd

st.set_page_config(
    page_title="Prospect Theory Challenge",
    page_icon="🎯",
    layout="wide"
)

# -------------------------------------------------------
# CUSTOM CSS
# -------------------------------------------------------
st.markdown("""
<style>
.main {
    background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
    color: white;
}
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}
h1, h2, h3, h4 {
    color: #f8fafc !important;
}
.game-card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 20px;
    padding: 20px;
    margin-bottom: 18px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.25);
}
.option-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 16px;
    padding: 16px;
    min-height: 160px;
}
.metric-box {
    background: linear-gradient(135deg, #1d4ed8, #0ea5e9);
    border-radius: 18px;
    padding: 16px;
    color: white;
    text-align: center;
    font-weight: 700;
}
.small-note {
    color: #cbd5e1;
    font-size: 0.95rem;
}
.round-title {
    font-size: 1.4rem;
    font-weight: 800;
    color: #f8fafc;
}
.highlight {
    color: #fbbf24;
    font-weight: 700;
}
.result-good {
    background: rgba(34,197,94,0.15);
    border-left: 6px solid #22c55e;
    padding: 14px;
    border-radius: 12px;
}
.result-bad {
    background: rgba(239,68,68,0.15);
    border-left: 6px solid #ef4444;
    padding: 14px;
    border-radius: 12px;
}
.result-neutral {
    background: rgba(59,130,246,0.15);
    border-left: 6px solid #3b82f6;
    padding: 14px;
    border-radius: 12px;
}
.footer-box {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 16px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------
# GAME DATA
# -------------------------------------------------------
ROUNDS = [
    {
        "title": "Round 1 — The Safe Gain",
        "concept": "Risk Aversion in Gains",
        "scenario": "You are offered a reward. Choose the option you prefer.",
        "type": "binary",
        "option_a": {
            "label": "Take a sure gain of 500 points",
            "kind": "sure",
            "value": 500
        },
        "option_b": {
            "label": "50% chance to gain 1,000 points, 50% chance to gain 0",
            "kind": "gamble",
            "win_prob": 0.50,
            "win_value": 1000,
            "lose_value": 0
        },
        "theory_if_a": "You preferred certainty in the gain domain. This is classic Prospect Theory behavior.",
        "theory_if_b": "You accepted risk even though a sure gain was available. This is less common in the gain domain."
    },
    {
        "title": "Round 2 — The Painful Loss",
        "concept": "Risk Seeking in Losses",
        "scenario": "Now you must absorb a negative outcome. Choose the option you prefer.",
        "type": "binary",
        "option_a": {
            "label": "Take a sure loss of 500 points",
            "kind": "sure",
            "value": -500
        },
        "option_b": {
            "label": "50% chance to lose 1,000 points, 50% chance to lose 0",
            "kind": "gamble",
            "win_prob": 0.50,
            "win_value": 0,
            "lose_value": -1000
        },
        "theory_if_a": "You accepted the sure loss. This is more conservative than the usual pattern.",
        "theory_if_b": "You avoided the sure loss and took the gamble. This matches risk seeking in the loss domain."
    },
    {
        "title": "Round 3 — Positive Framing",
        "concept": "Framing Effect",
        "scenario": "A city faces a dangerous outbreak. A policy must be chosen for 600 people at risk.",
        "type": "binary",
        "option_a": {
            "label": "200 people will be saved for sure",
            "kind": "sure",
            "value": 200
        },
        "option_b": {
            "label": "1/3 probability that all 600 will be saved, 2/3 probability that nobody will be saved",
            "kind": "gamble",
            "win_prob": 1/3,
            "win_value": 600,
            "lose_value": 0
        },
        "theory_if_a": "You preferred the sure positive frame. Many people do the same.",
        "theory_if_b": "You accepted the risk in a positively framed problem."
    },
    {
        "title": "Round 4 — Negative Framing",
        "concept": "Framing Effect",
        "scenario": "The same outbreak problem is presented differently.",
        "type": "binary",
        "option_a": {
            "label": "400 people will die for sure",
            "kind": "sure",
            "value": -400
        },
        "option_b": {
            "label": "1/3 probability that nobody will die, 2/3 probability that all 600 will die",
            "kind": "gamble",
            "win_prob": 1/3,
            "win_value": 0,
            "lose_value": -600
        },
        "theory_if_a": "You accepted the sure negative outcome.",
        "theory_if_b": "You moved toward risk when the same problem was framed as losses. This is a classic framing effect."
    },
    {
        "title": "Round 5 — The Investor Trap",
        "concept": "Loss Aversion / Disposition Effect / Reference Point",
        "scenario": (
            "You bought a stock at 100. It has fallen to 80. "
            "The next trading day is uncertain. What do you do?"
        ),
        "type": "triple",
        "choices": [
            "Sell now and realize the loss",
            "Hold and wait for a rebound",
            "Buy more to reduce the average cost"
        ],
        "future_outcome": "The stock falls again from 80 to 68.",
        "theory_map": {
            "Sell now and realize the loss":
                "You realized the loss and avoided the emotional trap of reference dependence.",
            "Hold and wait for a rebound":
                "You kept the losing asset. This often reflects loss aversion and reluctance to realize losses.",
            "Buy more to reduce the average cost":
                "You increased risk in the loss domain. This is a strong Prospect Theory pattern."
        }
    }
]

# -------------------------------------------------------
# SESSION STATE
# -------------------------------------------------------
defaults = {
    "started": False,
    "player_name": "",
    "round_index": 0,
    "score": 2000,
    "history": [],
    "submitted": False,
    "last_feedback": "",
    "profile_tags": {
        "safe_gain": 0,
        "loss_gamble": 0,
        "framing_shift": 0,
        "hold_loser": 0,
        "average_down": 0
    }
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# -------------------------------------------------------
# HELPERS
# -------------------------------------------------------
def reset_game():
    st.session_state.started = True
    st.session_state.round_index = 0
    st.session_state.score = 2000
    st.session_state.history = []
    st.session_state.submitted = False
    st.session_state.last_feedback = ""
    st.session_state.profile_tags = {
        "safe_gain": 0,
        "loss_gamble": 0,
        "framing_shift": 0,
        "hold_loser": 0,
        "average_down": 0
    }

def resolve_option(option):
    if option["kind"] == "sure":
        return option["value"], f"Sure outcome: {option['value']} points"
    r = random.random()
    if r < option["win_prob"]:
        return option["win_value"], f"Chance outcome: {option['win_value']} points"
    return option["lose_value"], f"Chance outcome: {option['lose_value']} points"

def add_history(round_name, concept, choice, outcome, score_change, interpretation):
    st.session_state.history.append({
        "Round": round_name,
        "Concept": concept,
        "Choice": choice,
        "Outcome": outcome,
        "Score change": score_change,
        "Total score": st.session_state.score,
        "Interpretation": interpretation
    })

def get_profile():
    p = st.session_state.profile_tags
    parts = []

    if p["safe_gain"] >= 1:
        parts.append("certainty-seeking in gains")
    if p["loss_gamble"] >= 1:
        parts.append("risk-seeking in losses")
    if p["framing_shift"] >= 1:
        parts.append("sensitive to framing")
    if p["hold_loser"] >= 1:
        parts.append("reluctant to realize losses")
    if p["average_down"] >= 1:
        parts.append("willing to increase risk after losses")

    if not parts:
        return "relatively resistant to the classic Prospect Theory patterns in this short game"

    return ", ".join(parts)

# -------------------------------------------------------
# HEADER
# -------------------------------------------------------
st.title("🎯 Prospect Theory Challenge")
st.markdown(
    "<div class='small-note'>A fast individual decision game about gains, losses, framing, and investor psychology.</div>",
    unsafe_allow_html=True
)

# -------------------------------------------------------
# SIDEBAR
# -------------------------------------------------------
with st.sidebar:
    st.header("Game Control")
    st.session_state.player_name = st.text_input(
        "Player name",
        value=st.session_state.player_name,
        placeholder="Enter your name"
    )

    if not st.session_state.started:
        if st.button("Start Game", use_container_width=True):
            reset_game()
    else:
        if st.button("Restart Game", use_container_width=True):
            reset_game()

    st.markdown("---")
    st.metric("Current Score", st.session_state.score)
    st.metric("Round", f"{min(st.session_state.round_index + 1, len(ROUNDS))}/{len(ROUNDS)}")

# -------------------------------------------------------
# START SCREEN
# -------------------------------------------------------
if not st.session_state.started:
    st.markdown("<div class='game-card'>", unsafe_allow_html=True)
    st.subheader("How to Play")
    st.markdown("""
- You will face **5 decision rounds**.
- Each round is linked to a key idea from **Prospect Theory**.
- Choose quickly and honestly.
- Your score will change based on outcomes.
- At the end, the game will reveal your **behavioral profile**.
    """)
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# -------------------------------------------------------
# END SCREEN
# -------------------------------------------------------
if st.session_state.round_index >= len(ROUNDS):
    st.success("Game completed.")

    profile_text = get_profile()

    st.markdown("<div class='game-card'>", unsafe_allow_html=True)
    st.subheader("Your Behavioral Profile")
    st.markdown(
        f"**{st.session_state.player_name or 'Player'}**, in this game you appeared to be: "
        f"**{profile_text}**."
    )
    st.markdown(
        """
This does not mean your choices were "wrong."  
It means your decisions reflect patterns that Prospect Theory often predicts:

- people usually prefer **certainty in gains**
- people often become **more risk-seeking in losses**
- equivalent problems can trigger different choices when **framed differently**
- investors often **hold losers too long** or **average down**
        """
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        st.markdown("<div class='game-card'>", unsafe_allow_html=True)
        st.subheader("Decision History")
        st.dataframe(df, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='footer-box'>", unsafe_allow_html=True)
    st.markdown(
        f"### Final Score: {st.session_state.score}"
    )
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# -------------------------------------------------------
# GAME ROUND
# -------------------------------------------------------
round_data = ROUNDS[st.session_state.round_index]
progress = (st.session_state.round_index) / len(ROUNDS)
st.progress(progress)

top1, top2, top3 = st.columns([1.2, 1, 1])

with top1:
    st.markdown(
        f"<div class='metric-box'>Player<br><span style='font-size:1.1rem'>{st.session_state.player_name or 'Anonymous'}</span></div>",
        unsafe_allow_html=True
    )
with top2:
    st.markdown(
        f"<div class='metric-box'>Round<br><span style='font-size:1.1rem'>{st.session_state.round_index + 1} / {len(ROUNDS)}</span></div>",
        unsafe_allow_html=True
    )
with top3:
    st.markdown(
        f"<div class='metric-box'>Score<br><span style='font-size:1.1rem'>{st.session_state.score}</span></div>",
        unsafe_allow_html=True
    )

st.markdown("<div class='game-card'>", unsafe_allow_html=True)
st.markdown(f"<div class='round-title'>{round_data['title']}</div>", unsafe_allow_html=True)
st.markdown(f"**Concept:** <span class='highlight'>{round_data['concept']}</span>", unsafe_allow_html=True)
st.write(round_data["scenario"])

# -------------------------------------------------------
# BINARY ROUNDS
# -------------------------------------------------------
if round_data["type"] == "binary":
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='option-card'>", unsafe_allow_html=True)
        st.subheader("Option A")
        st.write(round_data["option_a"]["label"])
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='option-card'>", unsafe_allow_html=True)
        st.subheader("Option B")
        st.write(round_data["option_b"]["label"])
        st.markdown("</div>", unsafe_allow_html=True)

    choice = st.radio(
        "Choose your option:",
        ["A", "B"],
        horizontal=True,
        key=f"choice_{st.session_state.round_index}"
    )

    if not st.session_state.submitted:
        if st.button("Lock In Decision", type="primary", use_container_width=True):
            with st.spinner("Processing decision..."):
                time.sleep(1.2)

            selected_option = round_data["option_a"] if choice == "A" else round_data["option_b"]
            delta, outcome = resolve_option(selected_option)
            st.session_state.score += delta

            if choice == "A":
                interpretation = round_data["theory_if_a"]
            else:
                interpretation = round_data["theory_if_b"]

            # profile logic
            if st.session_state.round_index == 0 and choice == "A":
                st.session_state.profile_tags["safe_gain"] += 1
            if st.session_state.round_index == 1 and choice == "B":
                st.session_state.profile_tags["loss_gamble"] += 1
            if st.session_state.round_index == 3:
                prev_choice = None
                for item in st.session_state.history:
                    if item["Round"] == "Round 3 — Positive Framing":
                        prev_choice = item["Choice"]
                if prev_choice == "A" and choice == "B":
                    st.session_state.profile_tags["framing_shift"] += 1

            add_history(
                round_name=round_data["title"],
                concept=round_data["concept"],
                choice=choice,
                outcome=outcome,
                score_change=delta,
                interpretation=interpretation
            )

            st.session_state.last_feedback = interpretation
            st.session_state.submitted = True
            st.rerun()
    else:
        last = st.session_state.history[-1]

        box_class = "result-neutral"
        if last["Score change"] > 0:
            box_class = "result-good"
        elif last["Score change"] < 0:
            box_class = "result-bad"

        st.markdown(f"<div class='{box_class}'>", unsafe_allow_html=True)
        st.markdown(f"**Your choice:** {last['Choice']}")
        st.markdown(f"**Outcome:** {last['Outcome']}")
        st.markdown(f"**Score change:** {last['Score change']}")
        st.markdown(f"**Interpretation:** {last['Interpretation']}")
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("Next Round", use_container_width=True):
            st.session_state.round_index += 1
            st.session_state.submitted = False
            st.rerun()

# -------------------------------------------------------
# TRIPLE CHOICE ROUND
# -------------------------------------------------------
elif round_data["type"] == "triple":
    st.markdown("<div class='option-card'>", unsafe_allow_html=True)
    selected = st.radio(
        "Choose your action:",
        round_data["choices"],
        key="investment_choice"
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if not st.session_state.submitted:
        if st.button("Lock In Investment Decision", type="primary", use_container_width=True):
            with st.spinner("Simulating market outcome..."):
                time.sleep(1.4)

            # score logic
            if selected == "Sell now and realize the loss":
                delta = -100
            elif selected == "Hold and wait for a rebound":
                delta = -240
                st.session_state.profile_tags["hold_loser"] += 1
            else:
                delta = -420
                st.session_state.profile_tags["average_down"] += 1

            st.session_state.score += delta
            outcome = round_data["future_outcome"]
            interpretation = round_data["theory_map"][selected]

            add_history(
                round_name=round_data["title"],
                concept=round_data["concept"],
                choice=selected,
                outcome=outcome,
                score_change=delta,
                interpretation=interpretation
            )

            st.session_state.last_feedback = interpretation
            st.session_state.submitted = True
            st.rerun()
    else:
        last = st.session_state.history[-1]

        box_class = "result-bad" if last["Score change"] < 0 else "result-neutral"
        st.markdown(f"<div class='{box_class}'>", unsafe_allow_html=True)
        st.markdown(f"**Your choice:** {last['Choice']}")
        st.markdown(f"**Market result:** {last['Outcome']}")
        st.markdown(f"**Score change:** {last['Score change']}")
        st.markdown(f"**Interpretation:** {last['Interpretation']}")
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("Finish Game", use_container_width=True):
            st.session_state.round_index += 1
            st.session_state.submitted = False
            st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------
# MINI HISTORY PANEL
# -------------------------------------------------------
if st.session_state.history:
    st.markdown("<div class='game-card'>", unsafe_allow_html=True)
    st.subheader("Recent Decisions")
    mini_df = pd.DataFrame(st.session_state.history)
    st.dataframe(mini_df, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
