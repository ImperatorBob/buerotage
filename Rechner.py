import streamlit as st
import datetime
import calendar
import holidays

# --- 
# 1. Die Berechnungs-Logik (unverändert)
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

    # Getrennte Rückgabe von Infos und Endergebnis
    result_info = (
        f"Info: {total_werktage} Werktage (Mo-Fr), "
        f"davon {feiertage_auf_werktag} Feiertage.\n"
        f"Basis-Soll (100%): {basis_solltage:.2f} Tage."
    )
    
    return result_info, buero_tage_gerundet, f"{monat_nr}/{jahr}"

# --- 
# 2. Die GUI
# ---

st.set_page_config(layout="centered") 
st.title("Bürotage-Rechner")

# --- ÄNDERUNG 1: Dein angepasster Info-Text ---
with st.expander("ℹ️ Info zur Berechnung (Hier klicken)"):
    st.markdown("""
    Die Berechnung erfolgt nach diesen Vorgaben:

    **1. Basis Solltage (Ziel-Bürotage bei 100%):**
    `(Wochenstunden / 40) * 8`

    **2. Reduzierte Solltage (Aliquotierung):**
    `Basis Solltage * (Werktage - Abzüge) / Werktage`

    **Wobei:**
    * **"Werktage"** = Mo-Fr.
    * **"Abzüge"** = Feiertage (bundeseinheitliche werden automatisch erfasst) + Urlaub + Krank + Gleitzeit. Regionale Feiertage, Brauchtumstage, etc. bitte als Urlaub/Gleitzeit erfassen.
    * **Was zählt auch als Bürotag?** Tage wie Reisetage, Kickoffs, Betriebsversammlungen oder "krank aus Büro" bitte als **Krank-** oder **Gleitzeittag** erfassen, da sie die Anwesenheitspflicht ebenfalls reduzieren.
    
    **Weitere Details:**
    * Das Endergebnis wird kaufmännisch gerundet.
    * Detaillierte Sonderfälle findest du im [internen FAQ](http://placeholder-link.intern/faq) (Nur per Intranet/VPN erreichbar).
    """)
# --- ENDE DES INFO-BEREICHS ---


# Monatsnamen und Mapping
MONTH_NAMES = ["Januar", "Februar", "März", "April", "Mai", "Juni", 
               "Juli", "August", "September", "Oktober", "November", "Dezember"]
MONTH_MAP = {name: i+1 for i, name in enumerate(MONTH_NAMES)}

# Aktuelles Datum holen
now = datetime.datetime.now()

# --- EINGABEFELDER (unverändert) ---

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

hours_val = st.number_input(
    "Wochenstunden:", 
    value=38.5, 
    step=0.5,
    min_value=0.0,
    max_value=40.0 
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
        info_text, final_days, month_year_str = get_calculation(
            year_val, month_val, hours_val, 
            sick_val, vacation_val, flex_val
        )
        
        # 1. Die Detail-Info in einer grünen Box (unverändert)
        st.success(info_text) 
        
        st.markdown("---") # Trennlinie
        
        # --- ÄNDERUNG 2: Grafische Anzeige mit roter Schrift ---
        st.markdown(
            f"""
            <div style="background-color: #0E1117; border: 1px solid #262730; border-radius: 10px; padding: 20px; text-align: center; margin-top: 20px;">
                <p style="font-size: 1.1rem; color: #FAFAFA; margin-bottom: 5px;">Dein Soll für {month_year_str}</p>
                <p style="font-size: 2.8rem; font-weight: bold; color: #FF4B4B; margin: 0;">{final_days} Tage</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        # --- ENDE DER GRAFISCHEN ANZEIGE ---

    except Exception as e:
        st.error(f"Fehler bei der Eingabe: {e}")
