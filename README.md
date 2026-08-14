# Boundary-Matter – TIMDR Framework

**Eksperymentalny silnik decyzyjny na danych giełdowych: generuje trzy sprzeczne tezy zamiast jednej prognozy, plus statystyczne sygnały anomalii (TIMDR Market).**

---

## Spis treści

1. [O projekcie](#o-projekcie)
2. [Co jest faktycznie zaimplementowane](#co-jest-faktycznie-zaimplementowane)
3. [Filozofia działania (warstwa koncepcyjna)](#filozofia-działania-warstwa-koncepcyjna)
4. [Wymagania](#wymagania)
5. [Instalacja i uruchomienie](#instalacja-i-uruchomienie)
6. [Endpointy API](#endpointy-api)
7. [Struktura projektu](#struktura-projektu)
8. [Przykład użycia](#przykład-użycia)
9. [Testy](#testy)
10. [Znane ograniczenia](#znane-ograniczenia)
11. [Możliwe kierunki rozwoju](#możliwe-kierunki-rozwoju)
12. [Licencja](#licencja)
13. [Załącznik: szkic koncepcyjny (spekulacyjny)](#załącznik-szkic-koncepcyjny-spekulacyjny)

---

## O projekcie

**Boundary-Matter** to framework do analizy danych giełdowych, który zamiast jednej prognozy generuje **trzy sprzeczne tezy** (kontratrendową, ambiwalentną, samospełniającą) — każda z własnym prawdopodobieństwem i rekomendacją — plus niezależny zestaw statystycznych sygnałów anomalii (**TIMDR Market**: nagłe zmiany ceny, anomalie wolumenu, lokalny trend, okresowość wolumenu).

Projekt korzysta z **rzeczywistych danych giełdowych** przez Yahoo Finance (yfinance) — to już działa, nie jest to element planowany na przyszłość.

---

## Co jest faktycznie zaimplementowane

Poniższa tabela opisuje **rzeczywisty stan kodu w tym repozytorium**, nie architekturę docelową:

| Plik | Co robi |
|---|---|
| `data_fetcher.py` | Pobiera dane OHLCV z Yahoo Finance (`yfinance`) lub opcjonalnie Alpha Vantage. |
| `api.py` | FastAPI — endpointy `/predict`, `/signal`, `/ohlcv`, `/timdr_market`, `/health`. Generuje 3 tezy, prosty sygnał KUP/SPRZEDAJ/TRZYMAJ (na SMA10/SMA30 + korekta o `k`), oraz sygnały TIMDR Market. |
| `app.py` | Dashboard Streamlit — łączy się z `api.py` (**wymaga uruchomionego API**, nie działa offline), pokazuje wykres ceny, metryki, tezy, sygnał handlowy i sygnały TIMDR Market. |
| `timdr_market.py` | `TIMDRMarket` — analiza sygnałów na świecach OHLCV: `twist_price()` (nagłe zmiany ceny), `anomaly_volume()` (anomalie wolumenu), `trend_price()` (lokalne nachylenie ceny w kroczącym oknie), `rhythm_volume()` (okresowość wolumenu). Wszystko oparte o statystykę MAD-zscore, nie o uczenie maszynowe. |
| `test_timdr_market.py` | 15 testów pytest dla `timdr_market.py` — testy regresyjne konkretnych błędów (patrz [Testy](#testy)), nie testy dokładności predykcji. |
| `run.bat` | Instaluje zależności i uruchamia jednocześnie API (port 8000) i dashboard (port 8501). |

Komponenty wymienione w poprzedniej wersji tego README (**TRM-Geometry-Core**, **TMME**, **TIV jako osobny moduł**, **J jako generator narracji**, **GSF**) oraz pliki konfiguracyjne (`boundary_filters_v2.json`, `tmme_deltas.json`, `theses_k-075.json`, `comparison_k_plus_vs_minus.json`) **nie istnieją w tym repozytorium** — były opisane jako architektura docelowa, nie stan obecny. Generowanie tez i sygnału handlowego dzieje się dziś wprost w `api.py` (funkcje `generate_theses()`, `generate_signal()`), bez oddzielnych modułów.

---

## Filozofia działania (warstwa koncepcyjna)

Ta sekcja opisuje **ramę pojęciową**, którą posługuje się projekt do nazywania swoich parametrów — nie jest to zweryfikowane prawo fizyczne ani ekonomiczne, tylko słownik używany w kodzie i komunikatach.

W trybie **lewoskrętnym (`k < 0`)** system:

- traktuje `k` jako "opóźnienie fazowe" wpływające na próg pewności sygnału,
- wzmacnia wagę sygnałów spadkowych względem wzrostowych (patrz `generate_signal()` w `api.py` — korekta prawdopodobieństwa o `abs(k) * 15`),
- generuje bardziej ostrożne (niższe prawdopodobieństwo) rekomendacje KUP.

Parametr `k` (zakres -1.50 do -0.50 w interfejsie) jest głównym suwakiem eksploracji w Streamlit.

**Warstwy Λ–τ–ρ** i **Boundary Ratios** (`R_n = n³ / ((n+1)³ - 1)`) z poprzedniej wersji README to warstwa nazewnicza/interpretacyjna, na razie **nie przekłada się na konkretny kod** w tym repozytorium — `k` jest pojedynczą liczbą zmiennoprzecinkową używaną bezpośrednio w `generate_signal()`/`generate_theses()`, nie ma osobnego modułu liczącego Λ, τ czy ρ. Jeśli to ma się zmienić, warto to zaimplementować jako osobny, testowalny moduł (podobnie jak `timdr_market.py`), zamiast trzymać tylko w dokumentacji.

---

## Wymagania

- Python 3.10+ (przetestowane; `run.bat`/`.pyc` w repo wskazują na 3.11, ale kod nie używa niczego specyficznego dla 3.11)
- pip

---

## Instalacja i uruchomienie

```bash
git clone https://github.com/jbackk-lang/Boundary-Matter.git
cd Boundary-Matter
pip install -r requirements.txt
```

### Najprostsza opcja: `run.bat` (Windows)

Instaluje zależności i uruchamia **oba** serwisy naraz (API w jednym oknie, dashboard w drugim):

```bash
run.bat
```

### Ręcznie (dowolny system)

Dashboard **wymaga działającego API** — uruchom oba, w tej kolejności:

```bash
# terminal 1 — API (port 8000)
python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload

# terminal 2 — dashboard (port 8501)
python -m streamlit run app.py
```

Po uruchomieniu:
- API: http://localhost:8000 (dokumentacja Swagger pod `/docs`, generowana automatycznie przez FastAPI)
- Dashboard: http://localhost:8501

---

## Endpointy API

| Endpoint | Metoda | Opis |
|---|---|---|
| `/` | GET | Komunikat powitalny. |
| `/health` | GET | Status API. |
| `/predict` | POST | Pełna prognoza: metryki (SMA10/SMA30, zmiana %), 3 tezy, sygnał handlowy, **sygnały TIMDR Market**. |
| `/signal` | POST | Sam sygnał KUP/SPRZEDAJ/TRZYMAJ. |
| `/ohlcv` | POST | Surowe dane OHLCV (do wykresów). |
| `/timdr_market` | POST | Sam TIMDR Market: liczba i ostatnie punkty twist/anomalii wolumenu, bieżący trend, wykryta okresowość wolumenu. |

Wszystkie endpointy POST przyjmują `symbol` (np. `"EURPLN=X"`, dowolny ticker Yahoo Finance) i `period` (`1mo`/`3mo`/`6mo`/`1y`/`2y`/`5y`); `/predict` i `/signal` dodatkowo `k`.

---

## Struktura projektu

```
Boundary-Matter/
├── api.py                # FastAPI - endpointy, generate_theses(), generate_signal(),
│                          # compute_timdr_market_signals()
├── app.py                 # Dashboard Streamlit (łączy się z api.py przez HTTP)
├── data_fetcher.py        # fetch_yfinance() / fetch_alpha_vantage() - CLI/standalone
├── timdr_market.py        # TIMDRMarket - twist/anomalia/trend/rytm na OHLCV
├── test_timdr_market.py   # 15 testów pytest
├── requirements.txt
└── run.bat                 # Uruchamia API + dashboard jednocześnie
```

---

## Przykład użycia

1. Uruchom `run.bat` (albo API + dashboard ręcznie, patrz wyżej).
2. W przeglądarce otwórz http://localhost:8501.
3. Wpisz symbol (np. `EURPLN=X`, `AAPL`, `BTC-USD`) i okres, ustaw `k`, kliknij „Pobierz dane".
4. Zobaczysz: wykres ceny, metryki (SMA10/SMA30, zmiana %), trzy tezy z poziomami wejścia/stop-loss/take-profit, prosty sygnał KUP/SPRZEDAJ/TRZYMAJ, oraz sekcję „🌀 Sygnały TIMDR Market" (nagłe zmiany ceny, anomalie wolumenu, trend lokalny, okresowość wolumenu).

Albo bezpośrednio przez API:

```bash
curl -X POST http://localhost:8000/timdr_market \
  -H "Content-Type: application/json" \
  -d '{"symbol": "EURPLN=X", "period": "6mo"}'
```

---

## Testy

`test_timdr_market.py` — 15 testów pytest dla `timdr_market.py`, każdy odpowiada konkretnemu, zweryfikowanemu błędowi znalezionemu w code review (pełna historia w docstringu modułu). W skrócie:

- `_mad_zscore()` zwracał same zera, gdy odchylenie MAD wychodziło dokładnie 0 (typowy przypadek: pojedyncza anomalia na tle długiego spokojnego okresu) — niezależnie jak duża była zmiana, nigdy nic nie było wykrywane. Naprawione fallbackiem opartym na rozstępie wartości.
- `trend_price()` przy krótkiej historii zwracał niespójny typ (pojedynczą tablicę zamiast krotki `(slopes, z)`), co powodowało `ValueError` przy rozpakowaniu. Naprawione — teraz nawet krótka historia dostaje realne (kurczące się) oszacowanie nachylenia.
- `anomaly_volume()`/`rhythm_volume()` generowały `RuntimeWarning` na pustych danych zamiast czystego pustego wyniku.
- Osobny test potwierdza wykrywanie anomalii dokładnie na **najnowszej świecy** — kluczowe dla monitoringu na żywo.

Uruchomienie:

```bash
pytest test_timdr_market.py -v
```

**Uwaga:** to są testy poprawności kodu (czy funkcja robi to, co deklaruje, na skonstruowanych przypadkach), **nie testy trafności predykcji rynkowych**. Nie ma w repozytorium zwalidowanego backtestu ani metryk typu "dokładność kierunkowa" na prawdziwej historii — jeśli takie liczby się pojawią w dokumentacji, powinny być poparte odtwarzalnym skryptem backtestu, nie samą deklaracją.

---

## Znane ograniczenia

- `generate_signal()`/`generate_theses()` w `api.py` to proste reguły na SMA10/SMA30 + liniowa korekta o `k`, nie model statystyczny ani ML — traktuj tezy i sygnał jako punkt wyjścia do własnej analizy, nie gotową rekomendację inwestycyjną.
- `twist_price()` (próg z>3.5 na drugiej pochodnej ceny) daje ok. 10% fałszywych alarmów na czystym random walk bez żadnego realnego wydarzenia — to własność progu, nie błąd; jeśli to problem w praktyce, rozważ wyższy próg albo wygładzenie ceny przed różniczkowaniem.
- Format `candles` w `timdr_market.py` (kolumny `[open, high, low, close, volume, t]`, `t` na końcu) jest nietypowy względem większości bibliotek OHLCV (zwykle timestamp na początku) — używaj `candles_from_ohlcv()` do konwersji z formatu tego repo, nie podłączaj innych źródeł danych bez sprawdzenia kolejności kolumn.
- `t` w `candles_from_ohlcv()` to kolejny numer świecy sesji, nie prawdziwy timestamp — dla danych dziennych z yfinance oznacza to "numer dnia sesji" (bez weekendów/świąt), nie kalendarzowy numer dnia.
- Warstwy Λ–τ–ρ i Boundary Ratios to na razie tylko dokumentacja pojęciowa, nie działający kod (patrz [Filozofia działania](#filozofia-działania-warstwa-koncepcyjna)).

---

## Możliwe kierunki rozwoju

- [x] Podłączenie API danych rynkowych (Yahoo Finance) — zrobione, `data_fetcher.py`/`api.py`.
- [ ] Backtest na historycznych danych z odtwarzalnymi metrykami (zamiast deklarowanych liczb bez źródła).
- [ ] Implementacja Λ–τ–ρ jako faktycznego, testowalnego modułu (jeśli ma zostać częścią silnika, nie tylko dokumentacji).
- [ ] Wdrożenie w chmurze (AWS/GCP).
- [ ] Rozbudowa o formacje świecowe.
- [ ] Testy jednostkowe dla `api.py`/`app.py` (obecnie testy pokrywają tylko `timdr_market.py`).
- [ ] CI/CD.

---

## Licencja

MIT — możesz używać, modyfikować i dystrybuować, pod warunkiem zachowania informacji o autorze.

## Autor

Projekt powstał podczas sesji TIMDR (2026-08-05).

## Kontakt

W sprawach związanych z rozwojem, testami lub współpracą — otwórz issue w repozytorium.

*Boundary-Matter – nie daje odpowiedzi, daje perspektywy.*

---

## Załącznik: szkic koncepcyjny (spekulacyjny)

Poniższe diagramy ("Układy po helu") to spekulacyjny, poglądowy szkic powiązany z warstwą Boundary Ratios opisaną wyżej — **nie jest to model chemiczny ani fizyczny**, tylko wizualna notacja pojęciowa autora. Zostawione tu jako kontekst twórczy projektu, oddzielone od dokumentacji technicznej powyżej.

```
Legenda:
O   = komórka / helisa
-   = połączenie liniowe
|   = połączenie pionowe
[X] = znana cząstka
[?] = strukturalnie możliwe, brak klasycznego odpowiednika

--- 1. Pierwszy obieg (maksimum: hel) ---
[H]        [He]
 O          O=O

--- 2. Drugi obieg — układy 3-komórkowe ---
[Li]              [?] (układ boczny)
O=O-O                O
                       \
                        O=O

--- 3. Układy 4-komórkowe ---
[Be]         [?] (skręcony czworokąt)
O=O            O-O
| |             |  \
O=O            O---O

--- 4. Układy 5-komórkowe ---
[B]              [?] (pięciokomórkowy wachlarz)
O=O                 O=O
| |                 |  \
O=O-O               O---O
                      \
                       O

--- 5. Układy 6-komórkowe ---
[C]              [?] (heksagonalny pierścień)
O=O                 O-O-O
| |                 |   |
O=O                 O-O-O
| |
O=O

--- 6. Układy 7-komórkowe ---
[N]              [?] (7-komórkowy "kwiat")
O=O                   O
| |                  / \
O=O                 O-O-O
| |                  \|/
O=O-O                 O
                       |
                       O

--- 7. Układy 8-komórkowe ---
[O]              [?] (8-komórkowy pierścień z rdzeniem)
O=O                 O-O-O-O
| |                 |     |
O=O                 O-O-O-O
| |
O=O
| |
O=O

--- 8. Układy 9-komórkowe ---
[F]              [?] (9-komórkowa gwiazda)
O=O                    O
| |                  / | \
O=O                 O--O--O
| |                  \ | /
O=O                    O
| |                    |
O=O-O                  O

--- 9. Układy 10-komórkowe ---
[Ne]             [?] (10-komórkowy podwójny pierścień)
O=O                 O-O-O-O-O
| |                 |       |
O=O                 O-O-O-O-O
| |
O=O
| |
O=O
| |
O=O
```
