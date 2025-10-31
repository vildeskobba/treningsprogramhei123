import streamlit as st



st.set_page_config(page_title="Treningsprogram", layout="wide")

st.title("Treningsprogram")

øvelser = ["Knebøy", "Benkpress", "Markløft"]

for øvelse in øvelser:
    st.subheader(øvelse)
    for sett in range(1, 4):
        st.checkbox(f"Set {sett}", key=f"{øvelse}_{sett}")
