import streamlit as st

st.set_page_config(page_title="Treningsprogram", layout="wide")

st.title("Treningsprogram")

øvelser = ["Knebøy", "Benkpress", "Markløft"]
sett_per_øvelse = 3

# 1. lag alle keys vi skal bruke
alle_keys = []
for øvelse in øvelser:
    for sett in range(1, sett_per_øvelse + 1):
        key = f"{øvelse}_{sett}"
        alle_keys.append(key)
        # init default verdi i session_state hvis den ikke finnes
        if key not in st.session_state:
            st.session_state[key] = False

# 2. knapp for å resette alt
if st.button("Reset alle (uncheck alt)"):
    for key in alle_keys:
        st.session_state[key] = False
    st.rerun()

st.divider()

# 3. tegn boksene, men koble dem til session_state
for øvelse in øvelser:
    st.subheader(øvelse)
    cols = st.columns(sett_per_øvelse)
    for i, sett in enumerate(range(1, sett_per_øvelse + 1)):
        key = f"{øvelse}_{sett}"
        with cols[i]:
            st.checkbox(f"Set {sett}", key=key)
