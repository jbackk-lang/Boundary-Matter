import streamlit as st
import json
import pandas as pd
import plotly.express as px

# ------------------ KONFIGURACJA STRONY ------------------
st.set_page_config(
    page_title="TIMDR Dashboard (Realny)",
    page_icon="📊",
    layout="wide"
)

st.title("📊 TIMDR – Rzeczywisty Podgląd Sesji 2026-08-05")
st.caption("Tryb: lewoskrętny (k = -0.75) | Dane załadowane z lokalnych plików JSON")

# ------------------ FUNKCJE ŁADUJĄCE JSON ------------------
@st.cache_data
def load_json(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"❌ Brak pliku: {filename}")
        return None
    except json.JSONDecodeError:
        st.error(f"❌ Błąd składni JSON w pliku: {filename}")
        return None

# ------------------ WCZYTANIE DANYCH ------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    boundary = load_json("boundary_filters_v2.json")
    if boundary:
        st.metric("Boundary-Matter", "v2.0", "załadowany")

with col2:
    deltas = load_json("tmme_deltas.json")
    if deltas:
        st.metric("Macierz Delt", f"{len(deltas['deltas']['k'])} wartości", "załadowana")

with col3:
    theses = load_json("theses_k-075.json")
    if theses:
        st.metric("Tezy", f"{len(theses['theses'])}", "załadowane")

with col4:
    comparison = load_json("comparison_k_plus_vs_minus.json")
    if comparison:
        st.metric("Porównanie k", "k<0 vs k>0", "załadowane")

st.divider()

# ------------------ WIDOK 1: BOUNDARY-MATTER ------------------
if boundary:
    st.subheader("🛡️ Filtry Boundary-Matter (wersja 2.0)")
    col1, col2, col3 = st.columns(3)
    
    prog_vol = boundary["filters"]["volatility"]
    col1.metric("Zmienność – Ostrzeżenie", f"{prog_vol['warning']}%")
    col1.metric("Zmienność – Anomalia", f"{prog_vol['anomaly']}%")
    col1.metric("Zmienność – Krytyczna", f"{prog_vol['critical']}%")
    
    prog_vol = boundary["filters"]["volume"]
    col2.metric("Wolumen – Ostrzeżenie", f"{prog_vol['warning']}x")
    col2.metric("Wolumen – Anomalia", f"{prog_vol['anomaly']}x")
    col2.metric("Wolumen – Krytyczna", f"{prog_vol['critical']}x")
    
    if boundary["filters"]["volume"]["seasonal_adjustment"]:
        col3.metric("Korekta sezonowa (grudzień)", f"x{boundary['filters']['volume']['seasonal_adjustment']['multiplier']}")
    
    st.caption(f"Tryb uczenia: {'WŁĄCZONY' if boundary.get('learning_mode') else 'WYŁĄCZONY'}")

st.divider()

# ------------------ WIDOK 2: MACIERZ DELT (wykres) ------------------
if deltas:
    st.subheader("📈 Przesunięcie fazowe Δf(k) w zależności od skrętu")
    df_deltas = pd.DataFrame({
        "k": deltas["deltas"]["k"],
        "Δf (dni)": deltas["deltas"]["delta_f"],
        "Δσ (%)": deltas["deltas"]["delta_sigma"],
        "ΔH (bity)": deltas["deltas"]["delta_H"]
    })
    
    fig = px.line(
        df_deltas, 
        x="k", 
        y="Δf (dni)", 
        title="Δf(k) – przesunięcie fazowe",
        markers=True,
        labels={"k": "Siła skrętu (k)", "Δf (dni)": "Przesunięcie [dni]"}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    col1.metric("Indeks nieliniowości (NI)", f"{deltas['nonlinearity_index']:.2f}")
    col2.metric("WSF dla k=-0.75", f"{deltas['wsf_for_k-075']:.1f}")

st.divider()

# ------------------ WIDOK 3: TEZY ------------------
if theses:
    st.subheader("🧠 Wygenerowane tezy (k = -0.75)")
    st.caption(f"Dominanta: **{theses['dominant']}**")
    
    metryki = theses["metrics"]
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Optymizm (O)", f"{metryki['O']:.3f}")
    col2.metric("Pesymizm (P)", f"{metryki['P']:.3f}")
    col3.metric("Zastygnięcie (Z)", f"{metryki['Z']:.3f}")
    col4.metric("RSI_TRM", f"{metryki['RSI_TRM']:.1f}")
    col5.metric("WSF", f"{metryki['WSF']:.1f}")
    
    for t in theses["theses"]:
        with st.expander(f"Teza {t['id']}: {t['type']} (Prawdopodobieństwo: {t['probability']}%, Ufność: {t['confidence']}%)"):
            st.write(t['statement'])
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Rekomendacja", t['action'])
            if t.get('entry'):
                col_b.metric("Wejście", f"{t['entry']}")
                col_c.metric("Stop-loss / Take-profit", f"{t['stop_loss']} / {t['take_profit']}")
            else:
                col_b.write("(brak konkretnych poziomów)")
                col_c.write("(brak SL/TP)")

st.divider()

# ------------------ WIDOK 4: PORÓWNANIE k<0 vs k>0 ------------------
if comparison:
    st.subheader("⚖️ Porównanie trybów: k<0 (lewoskrętny) vs k>0 (prawoskrętny)")
    
    cmp = comparison["comparison"]
    df_cmp = pd.DataFrame({
        "Metryka": list(cmp.keys()),
        "k = -0.75": [cmp[m]["k_minus"] for m in cmp],
        "k = +0.75": [cmp[m]["k_plus"] for m in cmp],
        "Różnica": [cmp[m]["difference"] for m in cmp]
    })
    st.dataframe(df_cmp, use_container_width=True)
    
    st.caption("Uwagi jakościowe:")
    for key, val in comparison["qualitative_observations"].items():
        st.write(f"- **{key}:** {val}")

st.divider()
st.caption("✅ Dashboard oparty na rzeczywistych plikach JSON zapisanych na Twoim dysku. Wygenerowano: 2026-08-05")
