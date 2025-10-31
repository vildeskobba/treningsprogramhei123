import streamlit as st
import json
import os

st.set_page_config(page_title="Treningsprogram", layout="wide")
st.title("Treningsprogram")

DATAFIL = "progress.json"


def lag_standard_program():
    return [
        {"name": "Knebøy", "sets": 3},
        {"name": "Benkpress", "sets": 3},
        {"name": "Markløft", "sets": 3},
    ]


def load_data():
    if not os.path.exists(DATAFIL):
        # første gang
        return {
            "exercises": lag_standard_program(),
            "checks": {}
        }

    with open(DATAFIL, "r") as f:
        raw = json.load(f)

    # --- ny struktur allerede? ---
    if "exercises" in raw and "checks" in raw:
        return raw

    # --- gammel struktur -> migrer ---
    # gammel fil hadde bare checkbox-state, ingen liste med øvelser
    migrated = {
        "exercises": lag_standard_program(),
        "checks": raw if isinstance(raw, dict) else {}
    }
    return migrated


def save_data(data):
    with open(DATAFIL, "w") as f:
        json.dump(data, f)


# ---------- INIT STATE ----------
if "data" not in st.session_state:
    st.session_state.data = load_data()

# sørg for at alle checkbox-keys finnes både i data["checks"] og i st.session_state
for ex in st.session_state.data["exercises"]:
    # pass på at ex["sets"] er int
    ant_sett = int(ex["sets"])
    for s in range(1, ant_sett + 1):
        key = f"{ex['name']}_{s}"
        if key not in st.session_state.data["checks"]:
            st.session_state.data["checks"][key] = False
        if key not in st.session_state:
            st.session_state[key] = st.session_state.data["checks"][key]

# ---------- RESET KNAPP ----------
if st.button("Reset alle (uncheck alt)"):
    for ex in st.session_state.data["exercises"]:
        ant_sett = int(ex["sets"])
        for s in range(1, ant_sett + 1):
            key = f"{ex['name']}_{s}"
            st.session_state.data["checks"][key] = False
            st.session_state[key] = False
    save_data(st.session_state.data)
    st.rerun()

st.divider()

# ---------- VIS ØVELSER ----------
for ex in st.session_state.data["exercises"]:
    st.subheader(ex["name"])
    ant_sett = int(ex["sets"])
    cols = st.columns(ant_sett)

    for i, s in enumerate(range(1, ant_sett + 1)):
        key = f"{ex['name']}_{s}"
        with cols[i]:
            st.checkbox(f"Set {s}", key=key)

            # sync til persistent lagring
            if st.session_state.data["checks"][key] != st.session_state[key]:
                st.session_state.data["checks"][key] = st.session_state[key]
                save_data(st.session_state.data)

st.markdown("---")

# ---------- LEGG TIL NY ØVELSE ----------
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
        if nytt_navn.strip() != "":
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

            save_data(st.session_state.data)
            st.rerun()
