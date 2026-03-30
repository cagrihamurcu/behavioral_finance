import streamlit as st
import random
import pandas as pd

st.set_page_config(page_title="Prospect Theory Classroom Game", layout="wide")

# =========================================================
# DATA
# =========================================================
ROUNDS = [
    {
        "title": "Round 1 - Gain Domain",
        "type": "choice",
        "concept": "Risk aversion in gains / certainty effect",
        "scenario": (
            "You are offered two alternatives. Choose the one you prefer."
        ),
        "option_a": {
            "label": "A: Receive a sure gain of 500 points",
            "kind": "sure",
            "value": 500,
        },
        "option_b": {
            "label": "B: 50% chance to gain 1,000 points, 50% chance to gain 0",
            "kind": "gamble",
            "win_prob": 0.50,
            "win_value": 1000,
            "lose_value": 0,
        },
        "expected_pattern": "Most people prefer the sure gain.",
    },
    {
        "title": "Round 2 - Loss Domain",
        "type": "choice",
        "concept": "Risk seeking in losses / loss aversion",
        "scenario": (
            "Again, choose the option you prefer."
        ),
        "option_a": {
            "label": "A: Take a sure loss of 500 points",
            "kind": "sure",
            "value": -500,
        },
        "option_b": {
            "label": "B: 50% chance to lose 1,000 points, 50% chance to lose 0",
            "kind": "gamble",
            "win_prob": 0.50,
            "win_value": 0,
            "lose_value": -1000,
        },
        "expected_pattern": "Most people avoid the sure loss and choose the gamble.",
    },
    {
        "title": "Round 3 - Framing Effect (Positive Frame)",
        "type": "choice",
        "concept": "Framing effect",
        "scenario": (
            "A public policy must be chosen for a group of 600 people at risk."
        ),
        "option_a": {
            "label": "A: 200 people will be saved for sure",
            "kind": "sure",
            "value": 200,
        },
        "option_b": {
            "label": "B: 1/3 probability that 600 people will be saved, 2/3 probability that no one will be saved",
            "kind": "gamble",
            "win_prob": 1 / 3,
            "win_value": 600,
            "lose_value": 0,
        },
        "expected_pattern": "Most people prefer the sure positive outcome.",
    },
    {
        "title": "Round 4 - Framing Effect (Negative Frame)",
        "type": "choice",
        "concept": "Framing effect",
        "scenario": (
            "The same public policy problem is presented differently."
        ),
        "option_a": {
            "label": "A: 400 people will die for sure",
            "kind": "sure",
            "value": -400,
        },
        "option_b": {
            "label": "B: 1/3 probability that nobody will die, 2/3 probability that 600 people will die",
            "kind": "gamble",
            "win_prob": 1 / 3,
            "win_value": 0,
            "lose_value": -600,
        },
        "expected_pattern": "Many people switch preferences even though the problem is mathematically equivalent.",
    },
    {
        "title": "Round 5 - Investment Decision",
        "type": "portfolio",
        "concept": "Disposition effect / reference point / loss aversion",
        "scenario": (
            "You bought a stock at 100. It is now trading at 80. "
            "What do you want to do?"
        ),
        "choices": [
            "Sell now and realize the loss",
            "Hold and wait for recovery",
            "Buy more to reduce average cost",
        ],
        "next_move": -10,  # stock moves from 80 to 70
        "price_now": 80,
        "price_future": 70,
        "purchase_price": 100,
        "expected_pattern": "Many investors avoid realizing losses and keep holding or even buy more.",
    },
]

# =========================================================
# SESSION STATE
# =========================================================
if "player_name" not in st.session_state:
    st.session_state.player_name = ""

if "started" not in st.session_state:
    st.session_state.started = False

if "current_round" not in st.session_state:
    st.session_state.current_round = 0

if "score" not in st.session_state:
    st.session_state.score = 2000

if "history" not in st.session_state:
    st.session_state.history = []

if "round_submitted" not in st.session_state:
    st.session_state.round_submitted = False

if "class_counts" not in st.session_state:
    st.session_state.class_counts = {i: {"A": 0, "B": 0} for i in range(len(ROUNDS))}

if "portfolio_choice_counts" not in st.session_state:
    st.session_state.portfolio_choice_counts = {
        "Sell now and realize the loss": 0,
        "Hold and wait for recovery": 0,
        "Buy more to reduce average cost": 0,
    }

# =========================================================
# HELPER FUNCTIONS
# =========================================================
def reset_game():
    st.session_state.current_round = 0
    st.session_state.score = 2000
    st.session_state.history = []
    st.session_state.round_submitted = False
    st.session_state.started = True


def resolve_choice(option):
    if option["kind"] == "sure":
        return option["value"], f"Sure outcome: {option['value']} points"
    else:
        r = random.random()
        if r < option["win_prob"]:
            return option["win_value"], f"Gamble outcome: {option['win_value']} points"
        else:
            return option["lose_value"], f"Gamble outcome: {option['lose_value']} points"


def add_history(round_title, concept, choice, result_text, delta, explanation):
    st.session_state.history.append(
        {
            "Round": round_title,
            "Concept": concept,
            "Your choice": choice,
            "Outcome": result_text,
            "Points change": delta,
            "Score after round": st.session_state.score,
            "Interpretation": explanation,
        }
    )


def next_round():
    st.session_state.current_round += 1
    st.session_state.round_submitted = False


def interpretation_for_standard_round(round_data, selected_label):
    title = round_data["title"]

    if "Gain Domain" in title:
        if selected_label == "A":
            return (
                "You chose the sure gain. This is consistent with risk aversion in the gain domain "
                "and the certainty effect."
            )
        return (
            "You chose the gamble in the gain domain. This is a more risk-seeking response than what "
            "is usually observed."
        )

    if "Loss Domain" in title:
        if selected_label == "B":
            return (
                "You avoided the sure loss and chose the gamble. This is consistent with risk seeking "
                "in the loss domain."
            )
        return (
            "You accepted the sure loss. This is more conservative than the typical response."
        )

    if "Positive Frame" in title:
        if selected_label == "A":
            return (
                "You preferred the sure positive frame. This is a classic framing pattern."
            )
        return (
            "You accepted the probabilistic option even in a positive frame."
        )

    if "Negative Frame" in title:
        if selected_label == "B":
            return (
                "You chose the risky option under a negative frame. This is a classic framing effect response."
            )
        return (
            "You accepted the sure negative frame, which is less common in this setup."
        )

    return "Your choice reflects how prospect theory can shape preferences."


def portfolio_explanation(choice):
    if choice == "Sell now and realize the loss":
        return (
            "You realized the loss immediately. This is often emotionally difficult, but it avoids "
            "the common tendency to hold losing assets only because they are below the purchase price."
        )
    elif choice == "Hold and wait for recovery":
        return (
            "You kept the losing asset instead of realizing the loss. This is very common and is related "
            "to reference dependence and loss aversion."
        )
    else:
        return (
            "You increased exposure to a losing asset to reduce the average cost. This often reflects "
            "risk seeking in the loss domain."
        )


# =========================================================
# UI
# =========================================================
st.title("Prospect Theory Classroom Game")

st.markdown(
    """
This mini game helps students experience how **Prospect Theory** affects choices under
**gains, losses, framing, and investment decisions**.
"""
)

with st.sidebar:
    st.header("Game Panel")
    player_name = st.text_input("Student / Group Name", value=st.session_state.player_name)
    st.session_state.player_name = player_name

    if not st.session_state.started:
        if st.button("Start Game", use_container_width=True):
            reset_game()

    else:
        if st.button("Restart Game", use_container_width=True):
            reset_game()

    st.metric("Current Score", st.session_state.score)
    st.markdown(f"**Current Round:** {min(st.session_state.current_round + 1, len(ROUNDS))} / {len(ROUNDS)}")

# =========================================================
# BEFORE START
# =========================================================
if not st.session_state.started:
    st.info(
        "Enter a student or group name in the sidebar, then click **Start Game**."
    )
    st.stop()

# =========================================================
# GAME FINISHED
# =========================================================
if st.session_state.current_round >= len(ROUNDS):
    st.success("Game completed.")

    st.subheader("Final Reflection")
    st.markdown(
        """
- In gain situations, many people prefer **certainty**.
- In loss situations, many people become **more willing to gamble**.
- The same problem can produce different choices when it is **framed differently**.
- In investing, people often **sell winners too early** and **hold losers too long**.
"""
    )

    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        st.subheader("Your Decision History")
        st.dataframe(df, use_container_width=True)

    st.subheader("Teaching Note")
    st.markdown(
        """
This classroom game illustrates the core logic of Prospect Theory:

1. **Reference dependence**: people evaluate outcomes relative to a reference point.  
2. **Loss aversion**: losses hurt more than equivalent gains feel good.  
3. **Risk aversion in gains** and **risk seeking in losses** can coexist.  
4. **Framing matters** even when the underlying numbers are equivalent.
"""
    )
    st.stop()

# =========================================================
# CURRENT ROUND
# =========================================================
round_data = ROUNDS[st.session_state.current_round]

st.subheader(round_data["title"])
st.caption(f"Concept: {round_data['concept']}")
st.write(round_data["scenario"])

# =========================================================
# STANDARD CHOICE ROUNDS
# =========================================================
if round_data["type"] == "choice":
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Option A")
        st.write(round_data["option_a"]["label"])

    with col2:
        st.markdown("### Option B")
        st.write(round_data["option_b"]["label"])

    selected = st.radio(
        "Choose one option:",
        ["A", "B"],
        horizontal=True,
        key=f"radio_{st.session_state.current_round}",
    )

    if not st.session_state.round_submitted:
        if st.button("Submit Decision", type="primary"):
            st.session_state.class_counts[st.session_state.current_round][selected] += 1

            chosen_option = round_data["option_a"] if selected == "A" else round_data["option_b"]
            delta, result_text = resolve_choice(chosen_option)

            st.session_state.score += delta
            explanation = interpretation_for_standard_round(round_data, selected)

            add_history(
                round_title=round_data["title"],
                concept=round_data["concept"],
                choice=selected,
                result_text=result_text,
                delta=delta,
                explanation=explanation,
            )

            st.session_state.round_submitted = True
            st.rerun()

    else:
        last = st.session_state.history[-1]

        st.success("Decision recorded.")
        st.write(f"**Your choice:** {last['Your choice']}")
        st.write(f"**Outcome:** {last['Outcome']}")
        st.write(f"**Points change:** {last['Points change']}")
        st.write(f"**Interpretation:** {last['Interpretation']}")

        counts = st.session_state.class_counts[st.session_state.current_round]
        total = counts["A"] + counts["B"]

        st.markdown("### Classroom Response Snapshot")
        if total > 0:
            percent_a = 100 * counts["A"] / total
            percent_b = 100 * counts["B"] / total
            st.write(f"Option A: {counts['A']} responses ({percent_a:.1f}%)")
            st.write(f"Option B: {counts['B']} responses ({percent_b:.1f}%)")
        else:
            st.write("No classroom data yet.")

        st.info(f"Expected pattern: {round_data['expected_pattern']}")

        if st.button("Next Round"):
            next_round()
            st.rerun()

# =========================================================
# PORTFOLIO ROUND
# =========================================================
elif round_data["type"] == "portfolio":
    st.markdown(
        f"""
**Purchase price:** {round_data['purchase_price']}  
**Current price:** {round_data['price_now']}  
**Possible next observed price in this classroom simulation:** {round_data['price_future']}
"""
    )

    portfolio_choice = st.radio(
        "What would you do?",
        round_data["choices"],
        key="portfolio_choice",
    )

    if not st.session_state.round_submitted:
        if st.button("Submit Investment Decision", type="primary"):
            st.session_state.portfolio_choice_counts[portfolio_choice] += 1

            # Simple classroom payoff logic
            # Assume 100 shares were bought at 100.
            shares = 100
            current_price = round_data["price_now"]
            future_price = round_data["price_future"]

            if portfolio_choice == "Sell now and realize the loss":
                # Sell at current price
                delta = current_price * shares - round_data["purchase_price"] * shares
                result_text = (
                    f"You sold at {current_price}. Realized result: {delta} points relative to purchase."
                )
            elif portfolio_choice == "Hold and wait for recovery":
                delta = future_price * shares - round_data["purchase_price"] * shares
                result_text = (
                    f"You held the stock. It later moved to {future_price}. "
                    f"Position result: {delta} points relative to purchase."
                )
            else:
                # Buy 100 more at 80, then future price is 70
                avg_cost = (round_data["purchase_price"] * 100 + current_price * 100) / 200
                delta = (future_price - avg_cost) * 200
                result_text = (
                    f"You averaged down by buying more at {current_price}. "
                    f"New average cost: {avg_cost:.1f}. "
                    f"At future price {future_price}, total position result: {delta:.1f} points."
                )

            # Normalize impact on classroom score
            score_delta = int(delta / 20)
            st.session_state.score += score_delta

            explanation = portfolio_explanation(portfolio_choice)

            add_history(
                round_title=round_data["title"],
                concept=round_data["concept"],
                choice=portfolio_choice,
                result_text=result_text,
                delta=score_delta,
                explanation=explanation,
            )

            st.session_state.round_submitted = True
            st.rerun()

    else:
        last = st.session_state.history[-1]

        st.success("Investment decision recorded.")
        st.write(f"**Your choice:** {last['Your choice']}")
        st.write(f"**Outcome:** {last['Outcome']}")
        st.write(f"**Score impact:** {last['Points change']}")
        st.write(f"**Interpretation:** {last['Interpretation']}")

        st.markdown("### Classroom Response Snapshot")
        total = sum(st.session_state.portfolio_choice_counts.values())
        for k, v in st.session_state.portfolio_choice_counts.items():
            pct = (100 * v / total) if total > 0 else 0
            st.write(f"{k}: {v} responses ({pct:.1f}%)")

        st.info(f"Expected pattern: {round_data['expected_pattern']}")

        if st.button("Finish Game"):
            next_round()
            st.rerun()

# =========================================================
# HISTORY PANEL
# =========================================================
st.markdown("---")
st.subheader("Decision Log")

if st.session_state.history:
    hist_df = pd.DataFrame(st.session_state.history)
    st.dataframe(hist_df, use_container_width=True)
else:
    st.write("No decisions recorded yet.")
