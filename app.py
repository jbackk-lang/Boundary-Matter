"""
Boundary-Matter TIMDR Dashboard
Rzeczywiste dane z Yahoo Finance + interaktywna wizualizacja.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from data_fetcher import fetch_yfinance

# ------------------ KONFIGURACJA STRONY ------------------
st.set_page_config(
    page_title="TIMDR – Rzeczywiste dane",
    page_icon="📈",
    layout="wide"
)

st.title("📊 TIMDR – Boundary-Matter Dashboard")
st.caption("Tryb: lewoskrętny (k = -0.75) | Dane rzeczywiste z Yahoo Finance")

# ------------------ WIDGETY BOCZNE ------------------
with st.sidebar:
    st.header("⚙️ Konfiguracja")
    
    symbol = st.text_input("Symbol giełdowy", value="AAPL").upper()
    period = st.selectbox(
        "Okres danych",
        options=["1mo", "3mo", "6mo", "1y", "2y", "5y"],
        index=2  # domyślnie 6mo
    )
    
    k = st.slider(
        "Siła skrętu (k)",
        min_value=-1.50,
        max_value=-0.50,
        value=-0.75,
        step=0.01,
        help="Parametr lewoskrętny – ujemne wartości opóźniają cykle"
    )
    
    fetch_btn = st.button("🔄 Pobierz dane", type="primary", use_container_width=True)

# ------------------ STAN SESJI ------------------
if "data" not in st.session_state:
    st.session_state.data = None

# ------------------ POBIERANIE DANYCH ------------------
if fetch_btn or st.session_state.data is None:
    with st.spinner(f"Pobieranie {symbol} ({period})..."):
        try:
            raw = fetch_yfinance(symbol, period)
            st.session_state.data = raw
            st.success(f"✅ Pobrano {len(raw['close'])} dni dla {symbol}")
        except Exception as e:
            st.error(f"❌ Błąd: {e}")
            st.session_state.data = None

# ------------------ WYŚWIETLANIE DANYCH ------------------
data = st.session_state.data

if data is not None:
    # Podstawowe metryki
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Symbol", data["symbol"])
    col2.metric("Okres", data["period"])
    col3.metric("Dni", len(data["close"]))
    col4.metric("Ostatnia cena", f"${data['close'][-1]:.2f}")
    
    # Zmiana procentowa
    change = (data["close"][-1] / data["close"][0] - 1) * 100
    col5.metric("Zmiana", f"{change:.2f}%", delta=change)
    
    st.divider()
    
    # ------------------ WYKRES CEN ------------------
    st.subheader("📈 Wykres cen (OHLC)")
    df_price = pd.DataFrame({
        "Data": data["date"],
        "Otwarcie": data["open"],
        "Max": data["high"],
        "Min": data["low"],
        "Zamknięcie": data["close"]
    })
    # Konwersja dat dla czytelnego wykresu
    df_price["Data"] = pd.to_datetime(df_price["Data"])
    
    fig = px.line(
        df_price,
        x="Data",
        y="Zamknięcie",
        title=f"{data['symbol']} – cena zamknięcia",
        labels={"Zamknięcie": "Cena ($)", "Data": "Data"}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # ------------------ WOLUMEN ------------------
    st.subheader("📊 Wolumen")
    fig_vol = px.bar(
        df_price,
        x="Data",
        y=df_price.index,  # placeholder – faktycznie użyjemy wolumenu
        title="Wolumen dzienny"
    )
    # Niestety plotly nie wspiera direct volume z danych, więc poprawiamy:
    fig_vol = px.bar(
        x=df_price["Data"],
        y=data["volume"],
        labels={"x": "Data", "y": "Wolumen"}
    )
    st.plotly_chart(fig_vol, use_container_width=True)
    
    st.divider()
    
    # ------------------ SYMULOWANE METRYKI (na podstawie k) ------------------
    st.subheader("🧠 Generowane metryki (dla k = {:.2f})".format(k))
    
    # Tu można dodać prawdziwy moduł TIMDR, ale na razie generujemy przykładowe
    last_close = data["close"][-1]
    rsi_trm = 50 + k * 5  # uproszczona symulacja
    wsf = 15 + k * 2
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("RSI_TRM", f"{rsi_trm:.1f}")
    col2.metric("WSF", f"{wsf:.1f}")
    col3.metric("Optymizm (O)", f"{0.45 + k * 0.1:.3f}")
    col4.metric("Zastygnięcie (Z)", f"{0.70 - k * 0.1:.3f}")
    
    st.caption(f"Ostatnia aktualizacja: {data['last_update']} (czas lokalny)")

else:
    st.info("👈 Wybierz symbol i kliknij 'Pobierz dane'")

# ------------------ STOPKA ------------------
st.divider()
st.caption("Boundary-Matter / TIMDR Framework | Dane z Yahoo Finance")
