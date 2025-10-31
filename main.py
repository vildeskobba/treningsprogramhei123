import streamlit as st
import json
import os

st.set_page_config(page_title="Treningsprogram", layout="wide")
st.title("Treningsprogram")

DATAFIL = "progress.json"


def load_data():
    if os.path.exists(DATAFIL):
        with open(DATAFIL, "r") as f:
            return json.load(f)
    # første gang appen kjører
    return {
        "exercises": [
            {"name": "Knebøy", "sets": 3},
            {"name": "Benkpress", "sets": 3},
            {"name": "Markløft", "sets": 3},
        ],
        "checks": {}
    }


def save_data(data):
    with open(DATAFIL, "w") as f:
        json.dump(data, f)


# --- init i session_state ---
if "data" not in st.session_state:
    st.session_state.data = load_data()

# sørg for at alle checkbox-keys finnes både i data["checks"] og i st.session_state
for ex in st.session_state.data["exercises"]:
    for s in range(1, ex["sets"] + 1):
        key = f"{ex['name']}_{s}"
        if key not in st.session_state.data["checks"]:
            st.session_state.data["checks"][key] = False
        if key not in st.session_state:
            st.session_state[key] = st.session_state.data["checks"][key]

# --- reset knapp ---
if st.button("Reset alle (uncheck alt)"):
    for ex in st.session_state.data["exercises"]:
        for s in range(1, ex["sets"] + 1):
            key = f"{ex['name']}_{s}"
            st.session_state.data["checks"][key] = False
            st.session_state[key] = False
    save_data(st.session_state.data)
    st.rerun()

st.divider()

# --- vis øvelser og checkbokser ---
for ex in st.session_state.data["exercises"]:
    st.subheader(ex["name"])
    cols = st.columns(ex["sets"])
    for i, s in enumerate(range(1, ex["sets"] + 1)):
        key = f"{ex['name']}_{s}"
        with cols[i]:
            st.checkbox(f"Set {s}", key=key)
            # sync tilbake til persistent lagring
            if st.session_state.data["checks"][key] != st.session_state[key]:
                st.session_state.data["checks"][key] = st.session_state[key]
                save_data(st.session_state.data)

st.markdown("---")

st.subheader("Legg til ny øvelse")

with st.form("ny_øvelse_form"):
    nytt_navn = st.text_input(
        "Navn på øvelse (ta med reps i navnet hvis du vil, f.eks. 'Benkpress 8-8-6')",
        value=""
    )
    nytt_antall_sett = st.number_input(
        "Antall sett",
        min_value=1,
        max_value=10,
        step=1,
        value=3
    )

    submit = st.form_submit_button("Legg til øvelse")

    if submit:
        # bare legg til hvis navn ikke er tomt
        if nytt_navn.strip() != "":
            # legg øvelsen inn i lista
            ny_øvelse = {
                "name": nytt_navn.strip(),
                "sets": int(nytt_antall_sett),
            }
            st.session_state.data["exercises"].append(ny_øvelse)

            # init checkbokser for den nye øvelsen
            for s in range(1, ny_øvelse["sets"] + 1):
                key = f"{ny_øvelse['name']}_{s}"
                st.session_state.data["checks"][key] = False
                st.session_state[key] = False

            # lagre til disk
            save_data(st.session_state.data)

            # rerun for å vise den nye øvelsen med én gang
            st.rerun()
