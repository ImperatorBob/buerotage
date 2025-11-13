import streamlit as st
import datetime
import calendar
import holidays

# --- 
# 1. Die Berechnungs-Logik (Angepasst)
# ---
def get_calculation(jahr, monat_nr, wochenstunden, krank, urlaub, gleitzeit):
    """
    Diese Funktion enthält die reine Berechnungslogik.
    """
    
    try:
        num_days_in_month = calendar.monthrange(jahr, monat_nr)[1]
    except calendar.IllegalMonthError:
        return f"Fehler: Monat {monat_nr} ist ungültig."

    # Feiertage (bundeseinheitlich) holen
    german_holidays = holidays.country_holidays('DE', years=jahr)

    total_werktage = 0
    feiertage_auf_werktag = 0

    # Tage des Monats durchgehen
    for day in range(1, num_days_in_month + 1):
        current_date = datetime.date(jahr, monat_nr, day)
        weekday = current_date.weekday() # 0=Mo, 4=Fr
        
        if weekday < 5:  # Prüfen, ob Mo-Fr
            total_werktage += 1
            if current_date in german_holidays:
                feiertage_auf_werktag += 1

    # --- Die Berechnung ---
    basis_solltage = (wochenstunden / 40) * 8
    abzuege_gesamt = feiertage_auf_werktag + urlaub + gleitzeit + krank
    anrechenbare_tage = total_werktage - abzuege_gesamt

    if anrechenbare_tage < 0:
        anrechenbare_tage = 0

    if total_werktage > 0:
        buero_tage_real = basis_solltage * (anrechenbare_tage / total_werktage)
    else:
        buero_tage_real = 0

    buero_tage_gerundet = int(buero_tage_real + 0.5) # Kaufmännisch runden

    # --- ÄNDERUNG 3: Getrennte Rückgabe von Infos und Endergebnis ---
    
    # Text für die Info-Box
    result_info = (
        f"Info: {total_werktage} Werktage (Mo-Fr), "
        f"davon {feiertage_auf_werktag} Feiertage.\n"
        f"Basis-Soll (100%): {basis_solltage:.2f} Tage."
    )
    
    # Rückgabe als "Tupel" (Info-Text, Endergebnis, Monats-String)
    return result_info, buero_tage_gerundet, f"{monat_nr}/{jahr}"

# --- 
# 2. Die GUI
# ---

st.set_page_config(layout="centered") 
st.title("Bürotage-Rechner")

# --- ÄNDERUNG 2: Info-Text angepasst ---
with st.expander("ℹ️ Info zur Berechnung (Hier klicken)"):
    st.markdown("""
    Die Berechnung erfolgt nach diesen Vorgaben:

    **1. Basis Solltage (Ziel-Bürotage bei 100%):**
    `(Wochenstunden / 40) * 8`

    **2. Reduzierte Solltage (Aliquotierung):**
    `Basis Solltage * (Werktage - Abzüge) / Werktage`

    **Wobei:**
    * **"Werktage"** = Mo-Fr.
    * **"Abzüge"** = Feiertage (bundeseinheitl. auto) + Urlaub + Krank + Gleitzeit. Regionale Feiertage bitte als Urlaub/Gleitzeit erfassen.
    * **Was zählt nicht als Bürotag?** Tage wie Reisetage, Kickoffs, Betriebsversammlungen oder "krank aus Büro" bitte als **Krank-** oder **Gleitzeittag** erfassen, da sie die Anwesenheitspflicht reduzieren.
    * Das Endergebnis wird kaufmännisch gerundet.
    """)
# --- ENDE DES INFO-BEREICHS ---


# Monatsnamen und Mapping
MONTH_NAMES = ["Januar", "Februar", "März", "April", "Mai", "Juni", 
               "Juli", "August", "September", "Oktober", "November", "Dezember"]
MONTH_MAP = {name: i+1 for i, name in enumerate(MONTH_NAMES)}

# Aktuelles Datum holen
now = datetime.datetime.now()

# --- EINGABEFELDER ---

year_val = st.number_input(
    "Jahr:", 
    value=now.year, 
    step=1, 
    format="%d"
)

month_name = st.selectbox(
    "Monat:", 
    options=MONTH_NAMES, 
    index=now.month - 1
)

# --- ÄNDERUNG 1: Maximale Wochenstunden auf 40 begrenzt ---
hours_val = st.number_input(
    "Wochenstunden:", 
    value=38.5, 
    step=0.5,
    min_value=0.0,  # Min-Wert ist auch eine gute Praxis
    max_value=40.0  # Hier ist die Begrenzung
)

sick_val = st.number_input(
    "Kranktage:", 
    value=0, 
    step=1, 
    min_value=0
)

vacation_val = st.number_input(
    "Urlaubstage:", 
    value=0, 
    step=1, 
    min_value=0
)

flex_val = st.number_input(
    "Gleitzeittage:", 
    value=0, 
    step=1, 
    min_value=0
)


# --- Button und Berechnung ---
if st.button("Berechnen"):
    try:
        month_val = MONTH_MAP[month_name]
        
        # Logik-Funktion aufrufen
        # Wir "entpacken" die drei Rückgabewerte:
        info_text, final_days, month_year_str = get_calculation(
            year_val, month_val, hours_val, 
            sick_val, vacation_val, flex_val
        )
        
        # --- ÄNDERUNG 3: Angepasste Ergebnisanzeige ---
        
        # 1. Die Detail-Info in einer grünen Box
        st.success(info_text) 
        
        # 2. Das Endergebnis STARK hervorheben
        st.markdown(f"--- \n ### Dein Soll für {month_year_str}")
        st.metric(label="Bürotage", value=f"{final_days} Tage")
        # --- Ende der Ergebnisanzeige ---

    except Exception as e:
        st.error(f"Fehler bei der Eingabe: {e}")
