# timdr_market.py
"""
TIMDRMarket — analiza sygnalow TIMDR (twist/anomalia/trend/rytm) zastosowana
do danych gieldowych (OHLCV), analogicznie do modulu pogodowego SynoptykV4
(synoptyk-v2.0/analyzer/synoptyk_v4.py) - ten sam mechanizm MAD-zscore,
przeniesiony na inna domene.

Format wejsciowy `candles`: tablica 2D (n, 6) z kolumnami
[open, high, low, close, volume, t] - close=indeks 3, volume=indeks 4,
t=indeks 5 (ostatnia kolumna!). To NIE jest standardowy uklad OHLCV-z-
timestampem-na-poczatku uzywany np. przez ccxt/Binance - jesli podlaczasz
inne zrodlo danych niz `candles_from_ohlcv()` ponizej, upewnij sie ze
kolejnosc kolumn faktycznie sie zgadza, bo kod NIE waliduje uzycia i po
cichu przeczyta zle pola bez zadnego bledu.

`candles_from_ohlcv()` (nowa funkcja) buduje ta tablice z formatu slownik-
list-list uzywanego w tym repo przez data_fetcher.py/api.py
({'open':[...], 'high':[...], 'low':[...], 'close':[...], 'volume':[...]}) -
bez tego adaptera TIMDRMarket nie mial ZADNEGO polaczenia z reszta repo,
mimo ze api.py/app.py juz pobieraja dane w tym wlasnie formacie. `t` to
kolejny numer swiecy (0,1,2,...), NIE prawdziwy timestamp - dla danych
dziennych z yfinance to "numer dnia sesji", nie kalendarzowy (weekendy/
swieta sa pomijane w danych, wiec nachylenie z trend_price() jest "na
sesje", nie "na dzien kalendarzowy").

Ta wersja to polaczenie dwoch niezaleznie poprawionych iteracji (moja +
przeslana przez uzytkownika), zweryfikowanych wzajemnie tymi samymi
testami - patrz "Historia poprawek".

Historia poprawek (zweryfikowane testami, ten sam wzorzec bledow co w
analyzer/synoptyk_v3.py i synoptyk_v4.py z repo synoptyk-v2.0):

1. `_mad_zscore()`: gdy MAD (mediana |x - mediana(x)|) wychodzil dokladnie
   0, kod zwracal `np.zeros_like(x)` BEZWARUNKOWO - nie proporcjonalnie do
   wielkosci zmiany, tylko zawsze zero, niezaleznie jak duza byla zmiana.
   To normalny przypadek dla sparse eventu (nagly skok/anomalia) na tle
   dlugiego spokojnego okresu - typowa sytuacja dla wolumenu/ceny.
   Zweryfikowane: `twist_price()` na jednoznacznym skoku ceny +30 (na
   ostatniej swiecy, 100->130) zwracalo PUSTY wynik, z=0.0. `anomaly_
   volume()` na dniu z wolumenem x50 (50000 vs typowe 1000) - rowniez
   zero wykryc.
   Naprawione fallbackiem gdy MAD=0: skala z rozstepu (max-min)/4 -
   dobrana tak, ze wartosc najbardziej odstajaca zawsze dostaje z=4.0,
   wiec zawsze przebija progi 3.0/3.5 uzywane w tym module. Zweryfikowane
   rownolegle z alternatywnym fallbackiem (std()): oba dzialaja na tym
   samym zestawie testow (skok ceny, skok wolumenu, skok DOKLADNIE na
   ostatniej swiecy - kluczowe dla monitoringu na zywo, gradualny skok
   rozlozony na 2-30 swiec), obie metody go wykrywaja z zapasem powyzej
   progu. Test na 200 probach czystego random-walk (bez zadnego realnego
   wydarzenia) pokazuje ze fallback NIE zwieksza liczby falszywych alarmow
   tam gdzie ich wczesniej nie bylo - MAD=0 praktycznie nigdy nie
   wystepuje dla ciaglego szumu cenowego, wiec `twist_price()` ma taka
   sama (~10%, wlasciwosc progu z>3.5 na szumie przyspieszenia ceny, NIE
   efekt tej poprawki) czulosc na czysty szum przed i po zmianie.

2. `trend_price()`: gdy `n < window`, kod zwracal `np.zeros_like(close)` -
   POJEDYNCZA tablice, podczas gdy normalna sciezka zwraca `slopes, z` -
   KROTKE dwoch tablic. `slopes, z = trend_price(candles, window=20)` na
   10 swiecach rzucalo `ValueError: too many values to unpack`.
   Naprawione lepiej niz tylko zgodnym typem zwrotu: petla licząca
   nachylenie w oknie [max(0, i-window+1) : i+1] JUZ obsluguje krotsze
   okno przy i bliskim poczatku szeregu (kurczace sie okno zamiast pelnego
   `window`), wiec usunieto specjalny przypadek `n < window` w calosci -
   teraz nawet krotka historia dostaje realne (nie zerowe) oszacowania
   nachylenia. Zweryfikowane: n=10 przy window=20 daje poprawne, rosnace
   nachylenia zbiezne do prawdziwego trendu, zamiast samych zer.

3. `anomaly_volume()`/`rhythm_volume()`: brak guardu na pusta tablice -
   `np.median([])`/`np.mean([])` na pustym wolumenie generowalo
   `RuntimeWarning: Mean of empty slice`. Naprawione jawnymi, wczesnymi
   guardami na `candles.size == 0` PRZED jakimkolwiek dostepem do danych -
   w `rhythm_volume()` kolejnosc miala znaczenie: pierwsza wersja poprawki
   sprawdzala `n < 3` DOPIERO PO centrowaniu (`vol - np.mean(vol)`), wiec
   dla n=0 warning i tak sie pojawial, mimo ze funkcja poprawnie zwracala
   `[], 0.0` chwile pozniej - zweryfikowane testem, ktory to zlapal.

`rhythm_volume()` byl juz poprawnie znormalizowany wzgledem malejacego
nakladania sie probek przy rosnacym lag (dzielenie przez `overlap`,
analogicznie do poprawki 4 w synoptyk_v3.py) - nie wymagal zmian w samej
matematyce.

Nie w pelni rozwiazane (swiadomie, poza zakresem tej poprawki): sam prog
`z > 3.5` w `twist_price()` daje ~10% falszywych alarmow na czystym
random-walk (bez zadnego realnego wydarzenia) - to wlasciwosc progu przy
zaszumionej drugiej pochodnej ceny, nie regresja z tej poprawki (zmierzone
identycznie przed i po, oboma fallbackami). Jesli to problem w praktyce,
rozwazenie wyzszego progu albo wygladzania ceny przed rozniczkowaniem.
"""
import numpy as np


class TIMDRMarket:
    def __init__(self, mad_scale=1.4826):
        self.mad_scale = mad_scale

    # ---------- pomocnicze ----------
    def _mad_zscore(self, x):
        x = np.asarray(x, float)
        if x.size == 0:
            return np.zeros_like(x)
        med = np.median(x)
        mad = np.median(np.abs(x - med)) * self.mad_scale
        if mad == 0:
            # fallback - patrz "Historia poprawek", pkt 1: skala z rozstepu,
            # zeby skok na tle plaskiego sygnalu nie byl "niewidzialny".
            # /4.0 dobrane tak, ze najbardziej odstajaca wartosc dostaje
            # z=4.0 - z zapasem powyzej progow 3.0/3.5 uzywanych nizej.
            span = np.max(x) - np.min(x)
            if span == 0:
                return np.zeros_like(x)
            return (x - med) / (span / 4.0)
        return (x - med) / mad

    # ---------- TWIST: nagłe zmiany ceny ----------
    def twist_price(self, candles):
        candles = np.asarray(candles, float)
        if candles.size == 0 or candles.shape[0] < 3:
            return np.array([], int), np.array([], float)

        close = candles[:, 3]
        t = candles[:, 5]

        dprice = np.gradient(close, t)
        ddprice = np.gradient(dprice, t)

        z = np.abs(self._mad_zscore(ddprice))
        idx = np.where(z > 3.5)[0]
        return idx, z

    # ---------- ANOMALIE: wolumen ----------
    def anomaly_volume(self, candles):
        candles = np.asarray(candles, float)
        if candles.size == 0:  # NAPRAWIONE - patrz "Historia poprawek", pkt 3
            return np.array([], int), np.array([], float)

        vol = candles[:, 4]
        z = np.abs(self._mad_zscore(vol))
        idx = np.where(z > 3.0)[0]
        return idx, z

    # ---------- TREND: powolny dryf ceny ----------
    def trend_price(self, candles, window=20):
        candles = np.asarray(candles, float)
        close = candles[:, 3]
        t = candles[:, 5]

        n = len(t)
        slopes = np.zeros_like(close, dtype=float)
        if n < 2:  # NAPRAWIONE - patrz "Historia poprawek", pkt 2
            return slopes, np.zeros_like(slopes)

        for i in range(n):
            j0 = max(0, i - window + 1)
            tt = t[j0:i+1]
            cc = close[j0:i+1]
            A = np.column_stack([tt, np.ones_like(tt)])
            try:
                a, b = np.linalg.lstsq(A, cc, rcond=None)[0]
            except Exception:
                a = 0.0
            slopes[i] = a

        z = self._mad_zscore(slopes)
        return slopes, z

    # ---------- RHYTHM: periodyczność wolumenu ----------
    def rhythm_volume(self, candles, max_lag=60, power_thresh=0.4):
        candles = np.asarray(candles, float)
        if candles.size == 0:  # NAPRAWIONE - patrz "Historia poprawek", pkt 3
            return [], 0.0

        vol = candles[:, 4].astype(float)
        n = len(vol)
        if n < 3:
            return [], 0.0

        vol = vol - np.mean(vol)  # centrowanie - PO guardzie n<3, nie przed
        max_lag = min(max_lag, n - 1)
        ac = np.zeros(max_lag + 1)
        for lag in range(max_lag + 1):
            if lag == 0:
                ac[lag] = np.dot(vol, vol) / n
            else:
                overlap = n - lag
                if overlap <= 0:
                    break
                ac[lag] = np.dot(vol[:-lag], vol[lag:]) / overlap

        if ac[0] == 0:
            return [], 0.0
        ac /= ac[0]

        lags = np.arange(1, len(ac))
        power = ac[1:]
        dom_idx = np.where(power >= power_thresh)[0]
        if dom_idx.size == 0:
            return [], 0.0
        dom_periods = lags[dom_idx]
        beacon_score = float(power[dom_idx].max())
        return dom_periods.tolist(), beacon_score


def candles_from_ohlcv(ohlcv: dict) -> np.ndarray:
    """Buduje tablice `candles` (patrz docstring modulu) z formatu slownik-
    list-list zwracanego przez data_fetcher.fetch_yfinance()/api.fetch_
    yfinance() w tym repo. Bez tego TIMDRMarket nie ma polaczenia z
    reszta kodu - api.py/app.py juz pobieraja dane w tym formacie, wiec
    to jest brakujace ogniwo integracji."""
    n = len(ohlcv["close"])
    t = np.arange(n, dtype=float)
    return np.column_stack([
        np.asarray(ohlcv["open"], dtype=float),
        np.asarray(ohlcv["high"], dtype=float),
        np.asarray(ohlcv["low"], dtype=float),
        np.asarray(ohlcv["close"], dtype=float),
        np.asarray(ohlcv["volume"], dtype=float),
        t,
    ])
