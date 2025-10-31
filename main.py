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
    return {}  # tom første gang


def save_progress(progress_dict):
    with open(DATAFIL, "w") as f:
        json.dump(progress_dict, f)


# 1. last lagret progresjon fra fil (persistent)
if "progress" not in st.session_state:
    st.session_state.progress = load_progress()

# 2. sørg for at alle keys finnes i progress
for øvelse in øvelser:
    for sett in range(1, sett_per_øvelse + 1):
        key = f"{øvelse}_{sett}"
        if key not in st.session_state.progress:
            st.session_state.progress[key] = False

# 3. knapp for å resette alt
if st.button("Reset alle (uncheck alt)"):
    for key in st.session_state.progress.keys():
        st.session_state.progress[key] = False
    save_progress(st.session_state.progress)
    st.rerun()

st.divider()

# 4. tegn checkbokser OG oppdater progress når de endres
for øvelse in øvelser:
    st.subheader(øvelse)
    cols = st.columns(sett_per_øvelse)
    for i, sett in enumerate(range(1, sett_per_øvelse + 1)):
        key = f"{øvelse}_{sett}"

        with cols[i]:
            ny_verdi = st.checkbox(
                f"Set {sett}",
                value=st.session_state.progress[key],
                key=key
            )

            # hvis bruker klikker → oppdater lagring
            if ny_verdi != st.session_state.progress[key]:
                st.session_state.progress[key] = ny_verdi
                save_progress(st.session_state.progress)
