import streamlit as st
import pandas as pd
import random
import time

st.set_page_config(
    page_title="Prospect Trader: Beat Your Bias",
    page_icon="📉",
    layout="wide"
)

# ---------------------------------------------------------
# STYLING
# ---------------------------------------------------------
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: Arial, sans-serif;
}
.stApp {
    background: linear-gradient(180deg, #0b1220 0%, #111827 100%);
    color: #f3f4f6;
}
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}
h1, h2, h3 {
    color: #f9fafb !important;
}
.card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 18px;
    padding: 18px 20px;
    margin-bottom: 16px;
    box-shadow: 0 6px 24px rgba(0,0,0,0.18);
}
.hero {
    background: linear-gradient(135deg, #1d4ed8 0%, #0ea5e9 100%);
    border-radius: 22px;
    padding: 22px;
    color: white;
    margin-bottom: 16px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.25);
}
.metric-card {
    background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 16px;
    text-align: center;
    min-height: 110px;
}
.metric-label {
    font-size: 0.92rem;
    color: #cbd5e1;
    margin-bottom: 8px;
}
.metric-value {
    font-size: 1.6rem;
    font-weight: 800;
    color: #f9fafb;
}
.good-box {
    background: rgba(34,197,94,0.12);
    border-left: 6px solid #22c55e;
    border-radius: 12px;
    padding: 14px 16px;
    margin-top: 12px;
}
.bad-box {
    background: rgba(239,68,68,0.12);
    border-left: 6px solid #ef4444;
    border-radius: 12px;
    padding: 14px 16px;
    margin-top: 12px;
}
.neutral-box {
    background: rgba(59,130,246,0.12);
    border-left: 6px solid #3b82f6;
    border-radius: 12px;
    padding: 14px 16px;
    margin-top: 12px;
}
.option-box {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 14px;
    padding: 14px;
    min-height: 130px;
}
.small-note {
    color: #cbd5e1;
    font-size: 0.95rem;
}
.big-title {
    font-size: 2rem;
    font-weight: 900;
    margin-bottom: 6px;
}
.section-title {
    font-size: 1.2rem;
    font-weight: 800;
    margin-bottom: 10px;
}
.tag {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 700;
    margin-right: 6px;
    margin-bottom: 6px;
}
.tag-blue { background: rgba(59,130,246,0.18); color: #bfdbfe; }
.tag-red { background: rgba(239,68,68,0.18); color: #fecaca; }
.tag-yellow { background: rgba(245,158,11,0.18); color: #fde68a; }
.tag-green { background: rgba(34,197,94,0.18); color: #bbf7d0; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# GAME DATA
# ---------------------------------------------------------
ROUNDS = [
    {
        "title": "Round 1 — Small Sure Gain",
        "concept": "Risk Aversion in Gains",
        "status": "Gain Zone",
        "scenario": (
            "Your trading day starts well. You have a chance to lock in a modest gain "
            "or pursue a larger but uncertain result."
        ),
        "options": [
            {
                "label": "Secure the gain",
                "desc": "Take a sure gain of +80 points.",
                "kind": "sure",
                "value": 80,
                "bias": "certainty_preference",
                "teacher_note": "Many people prefer the sure gain in the gain domain."
            },
            {
                "label": "Take the risky trade",
                "desc": "50% chance of +180 points, 50% chance of 0.",
                "kind": "gamble",
                "win_prob": 0.50,
                "win_value": 180,
                "lose_value": 0,
                "bias": None,
                "teacher_note": "This choice is less typical in the gain domain."
            }
        ],
        "rational_note": "Expected value is +90 for the risky trade and +80 for the sure trade."
    },
    {
        "title": "Round 2 — Escape the Loss?",
        "concept": "Risk Seeking in Losses",
        "status": "Loss Zone",
        "scenario": (
            "A market shock pushes you below your emotional reference point. "
            "Now you must decide whether to accept a sure setback or gamble for escape."
        ),
        "options": [
            {
                "label": "Accept the damage",
                "desc": "Take a sure loss of -90 points.",
                "kind": "sure",
                "value": -90,
                "bias": None,
                "teacher_note": "This is more conservative than the common response."
            },
            {
                "label": "Try to escape",
                "desc": "50% chance of 0, 50% chance of -200 points.",
                "kind": "gamble",
                "win_prob": 0.50,
                "win_value": 0,
                "lose_value": -200,
                "bias": "loss_risk_seeking",
                "teacher_note": "Many people gamble to avoid locking in a sure loss."
            }
        ],
        "rational_note": "Expected value is -100 for the risky trade and -90 for the sure loss."
    },
    {
        "title": "Round 3 — Framing Trap",
        "concept": "Framing Effect",
        "status": "Decision Pressure",
        "scenario": (
            "You are shown a rescue policy for 600 affected people. The numbers are the same, "
            "but the language changes how the choice feels."
        ),
        "options": [
            {
                "label": "Choose the sure rescue",
                "desc": "200 people will be saved for sure.",
                "kind": "sure",
                "value": 70,
                "bias": "frame_safe",
                "teacher_note": "People often choose the sure option in a positive frame."
            },
            {
                "label": "Choose the risky rescue",
                "desc": "1/3 chance that all 600 will be saved, 2/3 chance that no one will be saved.",
                "kind": "gamble",
                "win_prob": 1/3,
                "win_value": 210,
                "lose_value": 0,
                "bias": None,
                "teacher_note": "This option has the same expected value but feels riskier."
            }
        ],
        "rational_note": "Both options have the same expected value in the original framing literature."
    },
    {
        "title": "Round 4 — The Losing Stock",
        "concept": "Disposition Effect / Loss Aversion",
        "status": "Loss Zone",
        "scenario": (
            "You bought a stock at 100. It is now at 76. You are under pressure because selling "
            "would make the loss real."
        ),
        "options": [
            {
                "label": "Sell now",
                "desc": "Realize the loss and move on. Score impact: -110 points.",
                "kind": "fixed",
                "value": -110,
                "bias": None,
                "teacher_note": "This avoids the common tendency to hold losers too long."
            },
            {
                "label": "Hold and hope",
                "desc": "Wait for recovery. In this simulation, the stock falls further. Score impact: -210 points.",
                "kind": "fixed",
                "value": -210,
                "bias": "hold_loser",
                "teacher_note": "Holding losers is a classic disposition effect pattern."
            },
            {
                "label": "Average down",
                "desc": "Buy more to reduce average cost. In this simulation, the stock falls further. Score impact: -320 points.",
                "kind": "fixed",
                "value": -320,
                "bias": "average_down",
                "teacher_note": "Increasing risk after losses is a strong Prospect Theory pattern."
            }
        ],
        "rational_note": "This round highlights reference dependence and the pain of realizing losses."
    },
    {
        "title": "Round 5 — Break-Even Hunter",
        "concept": "Reference Point / Break-Even Effect",
        "status": "Final Round",
        "scenario": (
            "You are near the end of the game. You are slightly below where you want to finish. "
            "Do you secure a respectable result or take a final gamble to get back above your mental target?"
        ),
        "options": [
            {
                "label": "Finish safely",
                "desc": "Take a sure gain of +60 points.",
                "kind": "sure",
                "value": 60,
                "bias": None,
                "teacher_note": "This is emotionally difficult when players focus on getting fully back to target."
            },
            {
                "label": "Go for break-even",
                "desc": "30% chance of +220 points, 70% chance of -120 points.",
                "kind": "gamble",
                "win_prob": 0.30,
                "win_value": 220,
                "lose_value": -120,
                "bias": "break_even_chasing",
                "teacher_note": "Players often chase recovery when they are close to the reference point."
            }
        ],
        "rational_note": "Expected value is -18 for the risky choice and +60 for the sure choice."
    }
]

# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------
DEFAULTS = {
    "started": False,
    "player_name": "",
    "round_index": 0,
    "wealth_score": 1000,
    "best_score": 1000,
    "benchmark": 1000,
    "bias_score": 0,
    "submitted": False,
    "history": [],
    "last_result": None,
    "profile": {
        "certainty_preference": 0,
        "loss_risk_seeking": 0,
        "frame_safe": 0,
        "hold_loser": 0,
        "average_down": 0,
        "break_even_chasing": 0
    }
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------
def reset_game() -> None:
    st.session_state.started = True
    st.session_state.round_index = 0
    st.session_state.wealth_score = 1000
    st.session_state.best_score = 1000
    st.session_state.benchmark = 1000
    st.session_state.bias_score = 0
    st.session_state.submitted = False
    st.session_state.history = []
    st.session_state.last_result = None
    st.session_state.profile = {
        "certainty_preference": 0,
        "loss_risk_seeking": 0,
        "frame_safe": 0,
        "hold_loser": 0,
        "average_down": 0,
        "break_even_chasing": 0
    }

def current_zone(score: int, benchmark: int) -> str:
    if score > benchmark:
        return "Gain Zone"
    if score < benchmark:
        return "Loss Zone"
    return "Neutral Zone"

def resolve_option(option: dict) -> tuple[int, str]:
    if option["kind"] in ("sure", "fixed"):
        return option["value"], f"Outcome: {option['value']:+d} points"
    draw = random.random()
    if draw < option["win_prob"]:
        return option["win_value"], f"Outcome: {option['win_value']:+d} points"
    return option["lose_value"], f"Outcome: {option['lose_value']:+d} points"

def add_history(round_title: str, concept: str, choice: str, outcome_text: str,
                wealth_change: int, theory: str, rational_note: str) -> None:
    st.session_state.history.append(
        {
            "Round": round_title,
            "Concept": concept,
            "Choice": choice,
            "Outcome": outcome_text,
            "Wealth Change": wealth_change,
            "Wealth Score": st.session_state.wealth_score,
            "Bias Score": st.session_state.bias_score,
            "Theory Insight": theory,
            "Rational Note": rational_note
        }
    )

def get_behavioral_profile() -> str:
    p = st.session_state.profile
    tags = []

    if p["certainty_preference"] > 0:
        tags.append("certainty-seeking in gains")
    if p["loss_risk_seeking"] > 0:
        tags.append("risk-seeking in losses")
    if p["frame_safe"] > 0:
        tags.append("frame-sensitive")
    if p["hold_loser"] > 0:
        tags.append("reluctant to realize losses")
    if p["average_down"] > 0:
        tags.append("willing to average down after losses")
    if p["break_even_chasing"] > 0:
        tags.append("prone to break-even chasing")

    if not tags:
        return "relatively disciplined and less influenced by classic Prospect Theory traps in this short simulation"
    return ", ".join(tags)

def result_box_class(change: int) -> str:
    if change > 0:
        return "good-box"
    if change < 0:
        return "bad-box"
    return "neutral-box"

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
with st.sidebar:
    st.header("Game Control")
    st.session_state.player_name = st.text_input(
        "Player Name",
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
    st.write("**Scoring System**")
    st.markdown("""
- **Wealth Score** = your game result  
- **Bias Score** = how often you fall into predicted behavioral traps  
- Lower **Bias Score** is better
    """)

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <div class="big-title">📉 Prospect Trader: Beat Your Bias</div>
        <div class="small-note">
            Survive 5 market days. Grow your score. Avoid psychological traps.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# START SCREEN
# ---------------------------------------------------------
if not st.session_state.started:
    c1, c2 = st.columns([1.25, 1])

    with c1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">How the Game Works</div>', unsafe_allow_html=True)
        st.markdown("""
You play as an individual trader across **5 market days**.

In each round:
- you face a market situation,
- choose one action,
- receive a point outcome,
- and learn what Prospect Theory predicts.

Your goal is to:
- finish with a high **Wealth Score**,
- keep your **Bias Score** low,
- and notice when your decisions are driven by psychology rather than logic.
        """)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Target</div>', unsafe_allow_html=True)
        st.markdown("""
- **Starting Score:** 1000  
- **Strong Finish:** 1200+  
- **Danger Zone:** Below 700  
- **Bias Goal:** As low as possible
        """)
        st.markdown("""
<span class="tag tag-blue">Reference Point</span>
<span class="tag tag-red">Loss Aversion</span>
<span class="tag tag-yellow">Framing</span>
<span class="tag tag-green">Disposition Effect</span>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.stop()

# ---------------------------------------------------------
# END SCREEN
# ---------------------------------------------------------
if st.session_state.round_index >= len(ROUNDS):
    profile = get_behavioral_profile()
    zone = current_zone(st.session_state.wealth_score, st.session_state.benchmark)

    st.success("Game completed.")

    top1, top2, top3, top4 = st.columns(4)
    metrics = [
        ("Final Wealth Score", st.session_state.wealth_score),
        ("Best Score Reached", st.session_state.best_score),
        ("Bias Score", st.session_state.bias_score),
        ("Final Zone", zone),
    ]
    for col, (label, value) in zip([top1, top2, top3, top4], metrics):
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Your Behavioral Profile</div>', unsafe_allow_html=True)
    st.write(
        f"**{st.session_state.player_name or 'Player'}**, in this simulation you appeared to be "
        f"**{profile}**."
    )
    st.markdown("""
**Interpretation**
- High wealth with low bias suggests more disciplined decision-making.
- High bias suggests that your decisions often matched Prospect Theory predictions.
- This does **not** mean your choices were irrational in every context.  
  It means your decisions were strongly influenced by framing, losses, or reference points.
    """)
    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.history:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Decision History</div>', unsafe_allow_html=True)
        df = pd.DataFrame(st.session_state.history)
        st.dataframe(df, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.stop()

# ---------------------------------------------------------
# CURRENT ROUND
# ---------------------------------------------------------
round_data = ROUNDS[st.session_state.round_index]
progress = st.session_state.round_index / len(ROUNDS)
st.progress(progress)

zone = current_zone(st.session_state.wealth_score, st.session_state.benchmark)
unrealized_vs_start = st.session_state.wealth_score - st.session_state.benchmark

m1, m2, m3, m4, m5 = st.columns(5)
metric_data = [
    ("Round", f"{st.session_state.round_index + 1}/{len(ROUNDS)}"),
    ("Wealth Score", st.session_state.wealth_score),
    ("Bias Score", st.session_state.bias_score),
    ("Best Score", st.session_state.best_score),
    ("Current Zone", zone),
]

for col, (label, value) in zip([m1, m2, m3, m4, m5], metric_data):
    with col:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown(f'<div class="section-title">{round_data["title"]}</div>', unsafe_allow_html=True)
st.write(f"**Concept:** {round_data['concept']}")
st.write(f"**Status:** {round_data['status']}")
st.write(round_data["scenario"])
st.markdown(f"**Change since start:** {unrealized_vs_start:+d} points")

# ---------------------------------------------------------
# OPTIONS DISPLAY
# ---------------------------------------------------------
option_labels = [opt["label"] for opt in round_data["options"]]
choice_lookup = {opt["label"]: opt for opt in round_data["options"]}

option_cols = st.columns(len(round_data["options"]))
for col, opt in zip(option_cols, round_data["options"]):
    with col:
        st.markdown('<div class="option-box">', unsafe_allow_html=True)
        st.write(f"**{opt['label']}**")
        st.write(opt["desc"])
        st.markdown("</div>", unsafe_allow_html=True)

selected_label = st.radio(
    "Choose your action:",
    option_labels,
    key=f"round_choice_{st.session_state.round_index}"
)

# ---------------------------------------------------------
# SUBMIT
# ---------------------------------------------------------
if not st.session_state.submitted:
    if st.button("Lock In Decision", type="primary", use_container_width=True):
        selected_option = choice_lookup[selected_label]

        with st.spinner("Market is reacting..."):
            time.sleep(1.2)

        wealth_change, outcome_text = resolve_option(selected_option)
        st.session_state.wealth_score += wealth_change
        st.session_state.best_score = max(st.session_state.best_score, st.session_state.wealth_score)

        if selected_option.get("bias"):
            st.session_state.bias_score += 1
            st.session_state.profile[selected_option["bias"]] += 1

        theory = selected_option["teacher_note"]

        add_history(
            round_title=round_data["title"],
            concept=round_data["concept"],
            choice=selected_label,
            outcome_text=outcome_text,
            wealth_change=wealth_change,
            theory=theory,
            rational_note=round_data["rational_note"]
        )

        st.session_state.last_result = {
            "choice": selected_label,
            "outcome_text": outcome_text,
            "wealth_change": wealth_change,
            "theory": theory,
            "rational_note": round_data["rational_note"],
        }
        st.session_state.submitted = True
        st.rerun()

# ---------------------------------------------------------
# RESULT
# ---------------------------------------------------------
else:
    result = st.session_state.last_result
    box_class = result_box_class(result["wealth_change"])

    st.markdown(f'<div class="{box_class}">', unsafe_allow_html=True)
    st.write(f"**Your choice:** {result['choice']}")
    st.write(f"**Score outcome:** {result['outcome_text']}")
    st.write(f"**Theory insight:** {result['theory']}")
    st.write(f"**Rational benchmark:** {result['rational_note']}")
    st.markdown("</div>", unsafe_allow_html=True)

    next_button_text = "Finish Game" if st.session_state.round_index == len(ROUNDS) - 1 else "Next Round"
    if st.button(next_button_text, use_container_width=True):
        st.session_state.round_index += 1
        st.session_state.submitted = False
        st.session_state.last_result = None
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# RECENT HISTORY
# ---------------------------------------------------------
if st.session_state.history:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Recent Decisions</div>', unsafe_allow_html=True)
    mini_df = pd.DataFrame(st.session_state.history)
    st.dataframe(mini_df, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
