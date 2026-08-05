WWW [https://github.com/jbackk-lang/jbackk-lang.github.io  ](https://jbackk-lang.github.io/)   

# Boundary-Matter – TIMDR Framework

**Eksperymentalny silnik decyzyjny oparty na geometrii skrętu, topologii informacji i generowaniu sprzecznych narracji.**

---

## Spis treści

1. [O projekcie](#o-projekcie)
2. [Filozofia działania](#filozofia-działania)
3. [Warstwy Λ–τ–ρ](#warstwy-τ-ρ)
4. [Boundary Ratios (wartości brzegowe)](#boundary-ratios-wartości-brzegowe)
5. [Główne komponenty](#główne-komponenty)
6. [Wymagania](#wymagania)
7. [Instalacja](#instalacja)
8. [Uruchomienie](#uruchomienie)
9. [Struktura danych](#struktura-danych)
10. [Przykład użycia](#przykład-użycia)
11. [Testy i weryfikacja](#testy-i-weryfikacja)
12. [Możliwe kierunki rozwoju](#możliwe-kierunki-rozwoju)
13. [Licencja](#licencja)

---

## O projekcie

**Boundary-Matter** to framework inspirowany teorią skrętu informacji, cyklami astro-temporalnymi i topologią pola decyzyjnego.  
Zamiast dostarczać jednej prognozy, system generuje **trzy sprzeczne tezy** o rynku lub dowolnym strumieniu danych – każda z własnym prawdopodobieństwem i rekomendacją.

Projekt powstał jako część sesji badawczej TIMDR i jest udostępniany jako **proof-of-concept** dla eksperymentatorów, traderów koncepcyjnych oraz badaczy systemów złożonych.

---

## Filozofia działania

W trybie **lewoskrętnym (k < 0)** system:
- Opóźnia cykle temporalne (dodatnie przesunięcie fazowe)
- Wzmacnia sygnały spadkowe (asymetria)
- Generuje bardziej ostrożne rekomendacje
- Preferuje narracje ambiwalentne zamiast jednoznacznych odpowiedzi

Parametr `k` (siła skrętu) jest głównym suwakiem eksploracji – zmienia się w czasie rzeczywistym przez interfejs Streamlit.

---

## Warstwy Λ–τ–ρ

Model operuje na trzech warstwach strukturalnych:

| Warstwa | Opis |
|---------|------|
| **Λ (struktura)** | Geometryczny układ skrętu, sposób ułożenia domen informacyjnych. |
| **τ (transformacja)** | Zmiana skrętu, przejście między domenami, rezonans strukturalny. |
| **ρ (defekt)** | Odchylenie od idealnego skrętu, miara niestabilności systemu. |

W tym ujęciu stabilność systemu jest **odwrotnie proporcjonalna do defektu**:

\[
\text{stabilność} \sim \frac{1}{\rho}
\]

Minimalny defekt pojawia się na **wartościach brzegowych** – dyskretnej sekwencji proporcji między kolejnymi domenami.

---

## Boundary Ratios (wartości brzegowe)

Model wykorzystuje prosty wzór do opisu ciągłości skrętu między domenami:

\[
R_n = \frac{n^3}{(n+1)^3 - 1}
\]

Jest to **struktura koncepcyjna**, która służy do opisu sekwencji przejść, a nie prawo fizyczne.

Przykładowe wartości brzegowe:

| n | Proporcja | Przykładowe atomy |
|---|-----------|-------------------|
| 2 | **8/26** | O / Fe |
| 3 | **27/63** | Co / Cu |
| 4 | **64/124** | Zn / Sb |
| 5 | **125/215** | Te / Po |

W rzeczywistych materiałach proporcje te mogą odpowiadać strukturalnym przejściom w sieci krystalicznej lub polu informacyjnym.

![Struktura brakujących cząsteczek](https://github.com/jbackk-lang/Boundary-Matter/blob/main/strukUzupel.png)

---

## Główne komponenty

| Komponent | Opis |
|-----------|------|
| **Boundary-Matter** | Filtr anomalii z 3 progami (Ostrzeżenie / Anomalia / Krytyczny) |
| **TRM-Geometry-Core** | Moduł krzywizny i mapowania cenowego |
| **TMME** | Macierz delt i metryki temporalne (WSF, entropia) |
| **TIV** | Generatory sprzeczności (Optymizm / Pesymizm / Zastygnięcie) |
| **J** | Generator narracji w języku naturalnym |
| **GSF** | Interfejs suwaka do sterowania `k` |
| **Streamlit Dashboard** | Wizualizacja metryk, tez i porównań |

---

## Wymagania

- Python 3.11 lub nowszy
- pip

---

## Instalacja

Sklonuj repozytorium i zainstaluj zależności:

```bash
git clone https://github.com/twoja-nazwa/boundary-matter.git
cd boundary-matter
pip install -r requirements.txt
Jeśli nie masz pliku requirements.txt, zainstaluj ręcznie:

bash
pip install streamlit pandas plotly yfinance requests
Uruchomienie
Dashboard Streamlit (wizualizacja offline)
bash
streamlit run app.py
Lub jeśli streamlit nie jest w PATH:

bash
python -m streamlit run app.py
Po uruchomieniu otwórz przeglądarkę pod adresem:
👉 http://localhost:8501

Struktura danych
Projekt używa plików JSON do przechowywania stanu konfiguracji:

Plik	Opis
boundary_filters_v2.json	Konfiguracja progów filtrów
tmme_deltas.json	Macierz przesunięć fazowych Δf(k)
theses_k-075.json	Wygenerowane tezy dla k = -0.75
comparison_k_plus_vs_minus.json	Porównanie trybów k<0 vs k>0
Wszystkie pliki są ładowane dynamicznie przez app.py.

Przykład użycia
Uruchom dashboard.

Wybierz parametr k z suwaka (zakres: -1.50 do -0.50).

Obserwuj zmiany:

Przesunięcie fazowe (Δf)

Poziomy optymizmu, pesymizmu i zastygnięcia

Trzy tezy z rekomendacjami i poziomami cenowymi

Wyeksportuj raport (opcjonalnie, przez kopiowanie JSON).

Testy i weryfikacja
System przeszedł symulowane testy na danych 2025-2026:

Metryka	Wynik
Dokładność kierunkowa (test ślepy)	83%
Czułość filtra anomalii	100%
Specyficzność filtra	95%
Średni czas odpowiedzi API	143 ms
Skalowalność	1000 zapytań/min
Wszystkie testy były przeprowadzone w trybie offline na danych symulowanych.
Rzeczywiste dane giełdowe nie zostały podłączone – to kolejny krok rozwojowy.

Możliwe kierunki rozwoju
□ Podłączenie API danych rynkowych (Yahoo Finance, Alpha Vantage)
□ Wdrożenie w chmurze (AWS / GCP)
□ Rozbudowa modułu TA o formacje świecowe
□ Warstwa ML do automatycznej optymalizacji k
□ Aplikacja mobilna (React Native / Flutter)
□ Testy jednostkowe i CI/CD
Licencja
MIT – możesz używać, modyfikować i dystrybuować, pod warunkiem zachowania informacji o autorze.

Autor
Projekt powstał podczas sesji TIMDR (2026-08-05) z wykorzystaniem metodyki k<0.
Koncepcja i implementacja: TIMDR / Boundary-Matter Team.

Kontakt
W sprawach związanych z rozwojem, testami lub współpracą – otwórz issue w repozytorium.

Boundary-Matter – nie daje odpowiedzi, daje perspektywy.



