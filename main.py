import streamlit as st
import json
import os

st.set_page_config(page_title="Vildes treningsprogram<3", layout="wide")
st.markdown(
    """
    <style>
        .stApp {
            background-color: #2e111a;
            color: white;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Vildes treningsprogram<3")

DATAFIL = "progress.json"


def lag_standard_program():
    return [
        {"name": "Eksempel-øvelse 1", "sets": 1},
        {"name": "Eksempel-øvelse 2", "sets": 2},
        {"name": "Eksempel-øvelse 3", "sets": 3},
    ]


def load_data():
    # struktur vi forventer:
    # {
    #   "exercises": [ { "name": "...", "sets": 3, "note": "..."? }, ... ],
    #   "checks": { "Benkpress_1": true, ... }
    # }
    if not os.path.exists(DATAFIL):
        return {
            "exercises": lag_standard_program(),
            "checks": {}
        }

    with open(DATAFIL, "r") as f:
        raw = json.load(f)

    # ny stil?
    if "exercises" in raw and "checks" in raw:
        return raw

    # gammel stil (bare checks)
    return {
        "exercises": lag_standard_program(),
        "checks": raw if isinstance(raw, dict) else {}
    }


def save_data(data):
    with open(DATAFIL, "w") as f:
        json.dump(data, f)


# ---------------- INIT STATE ----------------
if "data" not in st.session_state:
    st.session_state.data = load_data()

if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

# sørg for at alle checkbox-keys finnes både i persistent data["checks"] og i st.session_state
for ex in st.session_state.data["exercises"]:
    ant_sett = int(ex["sets"])
    for s in range(1, ant_sett + 1):
        key = f"{ex['name']}_{s}"
        if key not in st.session_state.data["checks"]:
            st.session_state.data["checks"][key] = False
        if key not in st.session_state:
            st.session_state[key] = st.session_state.data["checks"][key]


# ---------------- RESET ALLE ----------------
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

# ---------------- VIS OG KONTROLLER HVER ØVELSE ----------------
for idx, ex in enumerate(st.session_state.data["exercises"]):
    ant_sett = int(ex["sets"])

    # topplinje: navn, pil opp, pil ned, rediger/slett
    top_cols = st.columns([0.5, 0.1, 0.1, 0.3])

    with top_cols[0]:
        st.subheader(ex["name"])
        # vis notat hvis finnes
        if "note" in ex and ex["note"]:
            st.caption(ex["note"])

    with top_cols[1]:
        # flytt opp
        if st.button("⬆️", key=f"up_{idx}", help="Flytt opp"):
            if idx > 0:
                # bytt rekkefølge i lista
                lst = st.session_state.data["exercises"]
                lst[idx - 1], lst[idx] = lst[idx], lst[idx - 1]
                save_data(st.session_state.data)
                st.rerun()

    with top_cols[2]:
        # flytt ned
        if st.button("⬇️", key=f"down_{idx}", help="Flytt ned"):
            lst = st.session_state.data["exercises"]
            if idx < len(lst) - 1:
                lst[idx + 1], lst[idx] = lst[idx], lst[idx + 1]
                save_data(st.session_state.data)
                st.rerun()

    with top_cols[3]:
        if st.button("Rediger / Slett", key=f"editbtn_{idx}"):
            # toggle editor for denne øvelsen
            if st.session_state.edit_index == idx:
                st.session_state.edit_index = None
            else:
                st.session_state.edit_index = idx
            st.rerun()

    # checkbokser for set (horisontal rad slik du hadde)
    cols = st.columns(ant_sett)
    for i, s in enumerate(range(1, ant_sett + 1)):
        key = f"{ex['name']}_{s}"
        with cols[i]:
            st.checkbox(f"Set {s}", key=key)
            # sync fra session_state -> persistent lagring
            if st.session_state.data["checks"][key] != st.session_state[key]:
                st.session_state.data["checks"][key] = st.session_state[key]
                save_data(st.session_state.data)

    # editorpanel (bare synlig for valgt øvelse)
    if st.session_state.edit_index == idx:
        st.markdown("**Rediger denne øvelsen:**")
        with st.form(f"edit_form_{idx}"):

            nytt_navn = st.text_input(
                "Nytt navn (inkl reps i navnet hvis du vil)",
                value=ex["name"]
            )
            nytt_sett = st.number_input(
                "Antall sett",
                min_value=1,
                max_value=10,
                step=1,
                value=ant_sett
            )
            nytt_notat = st.text_area(
                "Notat (valgfritt)",
                value=ex.get("note", "")
            )

            col_edit = st.columns([0.4, 0.3, 0.3])
            with col_edit[0]:
                lagre = st.form_submit_button("Lagre endringer")
            with col_edit[1]:
                slett = st.form_submit_button("Slett øvelsen")
            with col_edit[2]:
                avbryt = st.form_submit_button("Avbryt")

        # trykk "lagre endringer"
        if lagre:
            gammelt_navn = ex["name"]
            gammelt_ant_sett = ant_sett
            nytt_antall_sett = int(nytt_sett)

            nytt_navn_clean = nytt_navn.strip()
            if nytt_navn_clean == "":
                nytt_navn_clean = gammelt_navn  # fallback så vi ikke tømmer navnet

            ny_ex = {
                "name": nytt_navn_clean,
                "sets": nytt_antall_sett,
                "note": nytt_notat.strip()
            }

            # bygg nye checkbox-keys for den redigerte øvelsen
            nye_checks_for_ex = {}
            for s in range(1, nytt_antall_sett + 1):
                gammel_key = f"{gammelt_navn}_{s}"
                ny_key = f"{ny_ex['name']}_{s}"

                if (
                    s <= gammelt_ant_sett
                    and gammel_key in st.session_state.data["checks"]
                ):
                    # behold eksisterende verdi
                    nye_checks_for_ex[ny_key] = st.session_state.data["checks"][gammel_key]
                else:
                    # nye sett starter som False
                    nye_checks_for_ex[ny_key] = False

            # fjern gamle keys fra både persistent og session_state
            for s in range(1, gammelt_ant_sett + 1):
                gammel_key = f"{gammelt_navn}_{s}"
                if gammel_key in st.session_state.data["checks"]:
                    del st.session_state.data["checks"][gammelt_key]
                if gammel_key in st.session_state:
                    del st.session_state[gammelt_key]

            # legg inn nye keys i persistent og session_state
            for key_name, val in nye_checks_for_ex.items():
                st.session_state.data["checks"][key_name] = val
                st.session_state[key_name] = val

            # oppdater selve øvelsen i lista
            st.session_state.data["exercises"][idx] = ny_ex

            save_data(st.session_state.data)

            # lukk editor
            st.session_state.edit_index = None
            st.rerun()

        # trykk "slett øvelsen"
        if slett:
            # slett alle checkbox-keys knyttet til denne øvelsen
            for s in range(1, ant_sett + 1):
                k = f"{ex['name']}_{s}"
                if k in st.session_state.data["checks"]:
                    del st.session_state.data["checks"][k]
                if k in st.session_state:
                    del st.session_state[k]

            # slett selve øvelsen
            st.session_state.data["exercises"].pop(idx)

            save_data(st.session_state.data)

            # lukk editor
            st.session_state.edit_index = None
            st.rerun()

        # trykk "avbryt"
        if avbryt:
            st.session_state.edit_index = None
            st.rerun()

    st.markdown("---")

# ---------------- LEGG TIL NY ØVELSE ----------------
st.subheader("Legg til ny øvelse")

with st.form("ny_øvelse_form"):
    nytt_navn = st.text_input(
        "Navn på øvelse (ta med antall reps i navnet)",
        value=""
    )
    nytt_antall_sett = st.number_input(
        "Antall sett",
        min_value=1,
        max_value=10,
        step=1,
        value=3
    )
    nytt_notat = st.text_area(
        "Notat (valgfritt)",
        value=""
    )

    submit = st.form_submit_button("Legg til øvelse")

    if submit:
        if nytt_navn.strip() != "":
            ny_øvelse = {
                "name": nytt_navn.strip(),
                "sets": int(nytt_antall_sett),
                "note": nytt_notat.strip()
            }

            # legg til i lista
            st.session_state.data["exercises"].append(ny_øvelse)

            # init checkbox-state for den nye øvelsen
            for s in range(1, ny_øvelse["sets"] + 1):
                key = f"{ny_øvelse['name']}_{s}"
                st.session_state.data["checks"][key] = False
                st.session_state[key] = False

            save_data(st.session_state.data)
            st.rerun()
