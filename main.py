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

    if "exercises" in raw and "checks" in raw:
        return raw

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

if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

# sørg for at alle checkbox-keys finnes både i data["checks"] og i st.session_state
for idx, ex in enumerate(st.session_state.data["exercises"]):
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

# ---------- VIS ØVELSER MED REDIGERING ----------
for idx, ex in enumerate(st.session_state.data["exercises"]):
    ant_sett = int(ex["sets"])

    # topp-linje med tittel + edit-knapp
    top_cols = st.columns([0.7, 0.3])
    with top_cols[0]:
        st.subheader(ex["name"])
    with top_cols[1]:
        if st.button("Rediger / Slett", key=f"editbtn_{idx}"):
            if st.session_state.edit_index == idx:
                st.session_state.edit_index = None
            else:
                st.session_state.edit_index = idx
            st.rerun()

    # checkbokser
    cols = st.columns(ant_sett)
    for i, s in enumerate(range(1, ant_sett + 1)):
        key = f"{ex['name']}_{s}"
        with cols[i]:
            st.checkbox(f"Set {s}", key=key)
            if st.session_state.data["checks"][key] != st.session_state[key]:
                st.session_state.data["checks"][key] = st.session_state[key]
                save_data(st.session_state.data)

    # editor for valgt øvelse
    if st.session_state.edit_index == idx:
        st.markdown("**Rediger denne øvelsen:**")
        with st.form(f"edit_form_{idx}"):

            nytt_navn = st.text_input(
                "Nytt navn (inkl reps om du vil)",
                value=ex["name"]
            )
            nytt_sett = st.number_input(
                "Antall sett",
                min_value=1,
                max_value=10,
                step=1,
                value=ant_sett
            )

            col_edit = st.columns([0.4, 0.3, 0.3])
            with col_edit[0]:
                lagre = st.form_submit_button("Lagre endringer")
            with col_edit[1]:
                slett = st.form_submit_button("Slett øvelsen")
            with col_edit[2]:
                avbryt = st.form_submit_button("Avbryt")

        if lagre:
            gammelt_navn = ex["name"]
            gammelt_ant_sett = ant_sett
            nytt_antall_sett = int(nytt_sett)

            ny_ex = {
                "name": nytt_navn.strip(),
                "sets": nytt_antall_sett
            }

            # bygg nye checkbox-keys
            nye_checks_for_ex = {}
            for s in range(1, nytt_antall_sett + 1):
                gammel_key = f"{gammelt_navn}_{s}"
                ny_key = f"{ny_ex['name']}_{s}"
                if (
                    s <= gammelt_ant_sett
                    and gammel_key in st.session_state.data["checks"]
                ):
                    nye_checks_for_ex[ny_key] = st.session_state.data["checks"][gammel_key]
                else:
                    nye_checks_for_ex[ny_key] = False

            # fjern gamle keys
            for s in range(1, gammelt_ant_sett + 1):
                gammel_key = f"{gammelt_navn}_{s}"
                if gammel_key in st.session_state.data["checks"]:
                    del st.session_state.data["checks"][gammel_key]
                if gammel_key in st.session_state:
                    del st.session_state[gammel_key]

            # legg til nye keys
            for key, val in nye_checks_for_ex.items():
                st.session_state.data["checks"][key] = val
                st.session_state[key] = val

            # oppdater selve øvelsen
            st.session_state.data["exercises"][idx] = ny_ex

            save_data(st.session_state.data)

            st.session_state.edit_index = None
            st.rerun()

        if slett:
            # slett alle checkboxer som tilhører denne øvelsen
            for s in range(1, ant_sett + 1):
                k = f"{ex['name']}_{s}"
                if k in st.session_state.data["checks"]:
                    del st.session_state.data["checks"][k]
                if k in st.session_state:
                    del st.session_state[k]

            # slett øvelsen fra lista
            st.session_state.data["exercises"].pop(idx)

            save_data(st.session_state.data)

            st.session_state.edit_index = None
            st.rerun()

        if avbryt:
            st.session_state.edit_index = None
            st.rerun()

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

            for s in range(1, ny_øvelse["sets"] + 1):
                key = f"{ny_øvelse['name']}_{s}"
                st.session_state.data["checks"][key] = False
                st.session_state[key] = False

            save_data(st.session_state.data)
            st.rerun()
