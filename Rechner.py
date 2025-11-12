import streamlit as st
import datetime
import calendar
import holidays
# (Hier deine 'get_calculation' Funktion von oben einfügen)
# ...
# def get_calculation(jahr, monat_nr, ...):
#     ...
#     return result_summary
# ...

# --- Ab hier beginnt die Streamlit GUI ---

st.title("Bürotage-Rechner")

# Monatsnamen und Mapping
MONTH_NAMES = ["Januar", "Februar", "März", "April", "Mai", "Juni", 
               "Juli", "August", "September", "Oktober", "November", "Dezember"]
MONTH_MAP = {name: i+1 for i, name in enumerate(MONTH_NAMES)}

# Aktuelles Datum holen
now = datetime.datetime.now()

# --- Eingabefelder ---
# Streamlit erstellt automatisch die GUI-Elemente

col1, col2 = st.columns(2) # Spalten für schöneres Layout

with col1:
    year_val = st.number_input(
        "Jahr:", 
        value=now.year, 
        step=1, 
        format="%d"
    )
    
    # Wochenstunden (bleibt float)
    hours_val = st.number_input(
        "Wochenstunden:", 
        value=38.5, 
        step=0.5
    )
    
    vacation_val = st.number_input(
        "Urlaubstage:", 
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
    
    sick_val = st.number_input(
        "Kranktage:", 
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
        result_text = get_calculation(
            year_val, month_val, hours_val, 
            sick_val, vacation_val, flex_val
        )
        
        # Ergebnis anzeigen
        st.success(result_text) # Zeigt eine grüne Box

    except Exception as e:

        st.error(f"Fehler bei der Eingabe: {e}")
