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
        return {"exercises": lag_standard_program(), "checks": {}}

    with open(DATAFIL, "r") as f:
        raw = json.load(f)

    if "exercises" in raw and "checks" in raw:
        return raw

    return {"exercises": lag_standard_program(), "checks": raw if isinstance(raw, dict) else {}}


def save_data(data):
    with open(DATAFIL, "w") as f:
        json.dump(data, f)


# ---------- INIT STATE ----------
if "data" not in st.session_state:
    st.session_state.data = load_data()

if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

for ex in st.session_state.data["exercises"]:
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
        for s in range(1, int(ex["sets"]) + 1):
            key = f"{ex['name']}_{s}"
            st.session_state.data["checks"][key] = False
            st.session_state[key] = False
    save_data(st.session_state.data)
    st.rerun()

st.divider()

# ---------- V
