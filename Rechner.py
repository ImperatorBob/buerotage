import streamlit as st
import datetime
import calendar
import holidays
# (Die 'tkinter' imports sind jetzt weg, da sie nicht mehr gebraucht werden)

# --- 
# 1. HIER IST DIE FEHLENDE FUNKTION (Lösung für den Fehler)
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

    # Ergebnis-Text formatieren und zurückgeben
    result_summary = (
        f"Info: {total_werktage} Werktage (Mo-Fr), "
        f"davon {feiertage_auf_werktag} Feiertage.\n"
        f"Basis-Soll (100%): {basis_solltage:.2f} Tage.\n"
        f"Dein Soll für {monat_nr}/{jahr}: {buero_tage_gerundet} Tage"
    )
    return result_summary

# --- 
# 2. HIER IST DIE GUI (Lösung für die Reihenfolge)
# ---

st.set_page_config(layout="centered") # Sorgt für bessere Darstellung auf Desktop
st.title("Bürotage-Rechner")

# Monatsnamen und Mapping
MONTH_NAMES = ["Januar", "Februar", "März", "April", "Mai", "Juni", 
               "Juli", "August", "September", "Oktober", "November", "Dezember"]
MONTH_MAP = {name: i+1 for i, name in enumerate(MONTH_NAMES)}

# Aktuelles Datum holen
now = datetime.datetime.now()

# --- NEUE REIHENFOLGE DER EINGABEFELDER ---
# Wir nutzen Spalten, damit es auf dem Handy gut aussieht

col1, col2 = st.columns(2) # Spalten für schöneres Layout

with col1:
    year_val = st.number_input(
        "Jahr:", 
        value=now.year, 
        step=1, 
        format="%d"
    )
    
    hours_val = st.number_input(
        "Wochenstunden:", 
        value=38.5, 
        step=0.5
    )
    
    sick_val = st.number_input(
        "Kranktage:", 
        value=0, 
        step=1, 
        min_value=0
    )


with col2:
    month_name = st.selectbox(
        "Monat:", 
        options=MONTH_NAMES, 
        index=now.month - 1
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
        
        # Logik-Funktion aufrufen (die jetzt oben definiert ist)
        result_text = get_calculation(
            year_val, month_val, hours_val, 
            sick_val, vacation_val, flex_val
        )
        
        # Ergebnis anzeigen
        st.success(result_text) # Zeigt eine grüne Box

    except Exception as e:
        st.error(f"Fehler bei der Eingabe: {e}")
