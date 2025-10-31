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
        return {
            "exercises": lag_standard_program(),
            "checks": {}
        }

    with open(DATAFIL, "r") as f:
        raw = json.load(f)

    # ny struktur?
    if "exercises" in raw and "checks" in raw:
        return raw

    # gammel struktur -> migrer
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

# aktiv editor (index til øvelse som er åpen i edit-modus)
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

# sørg for at alle checkbox-keys finnes både i data["checks"] og i st.session_state
for idx, ex in enumerate(st.session_state.data["exercises"]):
    ant_sett = int(ex["sets"]_
