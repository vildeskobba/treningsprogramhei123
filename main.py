import streamlit as st
import json
import os

st.set_page_config(page_title="Treningsprogram", layout="wide")
st.title("Treningsprogram")

øvelser = ["Knebøy", "Benkpress", "Markløft"]
sett_per_øvelse = 3
DATAFIL = "progress.json"


def load_progress():
    if os.path.exists(DATAFIL):
        with open(DATAFIL, "r") as f:
            return json.load(f)
    return {}


def save_progress(progress_dict):
    with open(DATAFIL, "w") as f:
        json.dump(progress_dict, f)


# --- init progress (persistent) ---
if "progress" not in st.session_state:
    st.session_state.progress = load_progress()

# sørg for at alle keys finnes i progress + session_state
for øvelse in øvelser:
    for sett in range(1, sett_per_øvelse + 1):
        key = f"{øvelse}_{sett}"
        if key not in st.session_state.progress:
            st.session_state.progress[key] = False
        if key not in st.session_state:
            st.session_state[key] = st.session_state.progress[key]

# --- reset knapp ---
if st.button("Reset alle (uncheck alt)"):
    # sett alt til False i begge steder
    for øvelse in øvelser:
        for sett in range(1, sett_per_øvelse + 1):
            key = f"{øvelse}_{sett}"
            st.session_state.progress[key] = False
            st.session_state[key] = False
    save_progress(st.session_state.progress)
    st.rerun()

st.divider()

# --- tegn checkbokser ---
for øvelse in øvelser:
    st.subheader(øvelse)
    cols = st.columns(sett_per_øvelse)
    for i, sett in enumerate(range(1, sett_per_øvelse + 1)):
        key = f"{øvelse}_{sett}"
        with cols[i]:
            # checkbox er bundet til st.session_state[key] automatisk pga key=
            st.checkbox(f"Set {sett}", key=key)

            # sync tilbake til progress (persistent) hver gang
            if st.session_state.progress[key] != st.session_state[key]:
                st.session_state.progress[key] = st.session_state[key]
                save_progress(st.session_state.progress)
