import streamlit as st
import json
import os

st.set_page_config(page_title="Vildes treningsprogram<3", layout="wide")
st.markdown(
    """
    <style>
        .stApp {
            background-color: #2e111a;
            color: #ffe9ec;
        }

        /* Tekstfarge i hele appen */
        *, label, p, span, h1, h2, h3, h4, h5, h6 {
            color: #ffe9ec !important;
        }

        /* Bokser og inputfelt */
        div[data-testid="stCheckbox"], 
        div[data-testid="stNumberInput"], 
        div[data-testid="stTextInput"],
        textarea, input {
            background-color: #2e111a !important;
            color: #ffe9ec !important;
        }

        /* Knapper */
        button[kind="primary"], button[kind="secondary"], button {
            background-color: #2e111a !important;
            color: #ffe9ec !important;
            border: 1px solid #ffe9ec !important;
        }

        /* Hover-effekt på knapper */
        button:hover {
            background-color: #471d29 !important;
        }
        /* Endre farge på checkboks når den er krysset av */
        div[data-testid="stCheckbox"] input[type="checkbox"] {
            accent-color: #ffb6c1 !important; /* lyserosa */
        }

        div[data-testid="stCheckbox"] > label > div[data-testid="stMarkdownContainer"] {
            color: #ffe9ec !important; /* behold lyserosa tekst */
        }

        /* Litt innrykk på checkboksene */
        div[data-testid="stCheckbox"] {
            margin-left: 20px;
        }


    </style>
    """,
    unsafe_allow_html=True
)

st.title("Vildes treningsprogram for verdens beste knær<3")

DATAFIL = "progress.json"


def lag_standard_program():
    return [
        {"name": "Eksempel-øvelse 1", "sets": 1, "reps": "10 reps"},
        {"name": "Eksempel-øvelse 2", "sets": 2, "reps": "12 reps"},
        {"name": "Eksempel-øvelse 3", "sets": 3, "reps": "8-10 reps"},
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

# Hent program fra JSON-knapp
if st.button("Hent program fra JSON"):
    st.session_state.data = load_data()

    for ex in st.session_state.data["exercises"]:
        ant_sett = int(ex["sets"])
        for s in range(1, ant_sett + 1):
            key = f"{ex['name']}_{s}"
            if key not in st.session_state.data["checks"]:
                st.session_state.data["checks"][key] = False
            st.session_state[key] = st.session_state.data["checks"][key]

    st.session_state.edit_index = None
    st.rerun()

# Reset alle checkbokser
if st.button("Reset alle sjekk-bokser"):
    for ex in st.session_state.data["exercises"]:
        ant_sett = int(ex["sets"])
        for s in range(1, ant_sett + 1):
            key = f"{ex['name']}_{s}"
            st.session_state.data["checks"][key] = False
            st.session_state[key] = False
    save_data(st.session_state.data)
    st.rerun()

# Proof of Concept mode toggle
if "poc_mode" not in st.session_state:
    st.session_state.poc_mode = False

st.session_state.poc_mode = st.toggle(
    "PoC mode",
    value=st.session_state.poc_mode
)

# sørg for at alle checkbox-keys finnes i session_state
for ex in st.session_state.data["exercises"]:
    ant_sett = int(ex["sets"])
    for s in range(1, ant_sett + 1):
        key = f"{ex['name']}_{s}"
        if key not in st.session_state.data["checks"]:
            st.session_state.data["checks"][key] = False
        if key not in st.session_state:
            st.session_state[key] = st.session_state.data["checks"][key]

st.divider()

# ---------------- VIS OG KONTROLLER HVER ØVELSE ----------------
for idx, ex in enumerate(st.session_state.data["exercises"]):
    ant_sett = int(ex["sets"])

    # topplinje: navn + reps + note
    top_cols = st.columns([1])
    with top_cols[0]:
        st.subheader(ex["name"])

        # ny linje: reps
        if "reps" in ex and ex["reps"]:
            st.text(f"{ex['reps']}")

        # note under reps
        if "note" in ex and ex["note"]:
            st.caption(ex["note"])

    # checkbokser for settene
    cols = st.columns(ant_sett)
    for i, s in enumerate(range(1, ant_sett + 1)):
        key = f"{ex['name']}_{s}"
        with cols[i]:
            st.checkbox(f"Set {s}", key=key)
            if st.session_state.data["checks"][key] != st.session_state[key]:
                st.session_state.data["checks"][key] = st.session_state[key]
                save_data(st.session_state.data)

    # KNAPPER UNDER SETTENE (bare i PoC mode)
    if st.session_state.poc_mode:
        btn_cols = st.columns(3)

        with btn_cols[0]:
            if st.button("⬆️", key=f"up_{idx}", help="Flytt opp"):
                if idx > 0:
                    lst = st.session_state.data["exercises"]
                    lst[idx - 1], lst[idx] = lst[idx], lst[idx - 1]
                    save_data(st.session_state.data)
                    st.rerun()

        with btn_cols[1]:
            if st.button("⬇️", key=f"down_{idx}", help="Flytt ned"):
                lst = st.session_state.data["exercises"]
                if idx < len(lst) - 1:
                    lst[idx + 1], lst[idx] = lst[idx], lst[idx + 1]
                    save_data(st.session_state.data)
                    st.rerun()

        with btn_cols[2]:
            if st.button("Rediger / Slett", key=f"editbtn_{idx}"):
                if st.session_state.edit_index == idx:
                    st.session_state.edit_index = None
                else:
                    st.session_state.edit_index = idx
                st.rerun()

    # editorpanel (bare i PoC mode + valgt øvelse)
    if st.session_state.poc_mode and st.session_state.edit_index == idx:
        st.markdown("**Rediger denne øvelsen:**")
        with st.form(f"edit_form_{idx}"):

            nytt_navn = st.text_input(
                "Nytt navn (f.eks 'Bulgarsk split squat 12 reps')",
                value=ex["name"]
            )
            nytt_reps = st.text_input(
                "Antall reps",
                value=ex.get("reps", "")
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

        if lagre:
            gammelt_navn = ex["name"]
            gammelt_ant_sett = ant_sett
            nytt_antall_sett = int(nytt_sett)

            nytt_navn_clean = nytt_navn.strip()
            if nytt_navn_clean == "":
                nytt_navn_clean = gammelt_navn

            ny_ex = {
                "name": nytt_navn_clean,
                "sets": nytt_antall_sett,
                "reps": nytt_reps.strip(),
                "note": nytt_notat.strip()
            }

            # bygg nye checkbox keys til denne øvelsen
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

            # legg inn nye keys
            for key_name, val in nye_checks_for_ex.items():
                st.session_state.data["checks"][key_name] = val
                st.session_state[key_name] = val

            # lagre ny info på øvelsen
            st.session_state.data["exercises"][idx] = ny_ex

            save_data(st.session_state.data)
            st.session_state.edit_index = None
            st.rerun()

        if slett:
            for s in range(1, ant_sett + 1):
                k = f"{ex['name']}_{s}"
                if k in st.session_state.data["checks"]:
                    del st.session_state.data["checks"][k]
                if k in st.session_state:
                    del st.session_state[k]

            st.session_state.data["exercises"].pop(idx)
            save_data(st.session_state.data)

            st.session_state.edit_index = None
            st.rerun()

        if avbryt:
            st.session_state.edit_index = None
            st.rerun()

    st.markdown("---")


# ---------------- LEGG TIL NY ØVELSE ----------------
if st.session_state.poc_mode:
    st.subheader("Legg til ny øvelse")

    with st.form("ny_øvelse_form"):
        nytt_navn = st.text_input(
            "Navn på øvelse",
            value=""
        )
        nytt_reps = st.text_input(
            "Antall reps",
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
                    "reps": nytt_reps.strip(),
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
