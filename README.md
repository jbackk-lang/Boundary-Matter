## 🔗 Wszystkie modele i repozytoria
Pełna lista projektów znajduje się na stronie:
https://jbackk-lang.github.io
---
# Boundary-Matter – TIMDR Framework

**Eksperymentalny silnik decyzyjny oparty na geometrii skrętu, topologii informacji i generowaniu sprzecznych narracji.**

---

## Spis treści

1. [O projekcie](#o-projekcie)
2. [Filozofia działania](#filozofia-działania)
3. [Główne komponenty](#główne-komponenty)
4. [Wymagania](#wymagania)
5. [Instalacja](#instalacja)
6. [Uruchomienie](#uruchomienie)
7. [Struktura danych](#struktura-danych)
8. [Przykład użycia](#przykład-użycia)
9. [Testy i weryfikacja](#testy-i-weryfikacja)
10. [Możliwe kierunki rozwoju](#możliwe-kierunki-rozwoju)
11. [Licencja](#licencja)

---

## O projekcie

**Boundary-Matter** to framework inspirowany teorią skrętu informacji, cyklami astro-temporalnymi i topologią pola decyzyjnego.  
Zamiast dostarczać jednej prognozy, system generuje **trzy sprzeczne tezy** o rynku lub dowolnym strumieniu danych – każda z własnym prawdopodobieństwem i rekomendacją.

Powstał jako część sesji badawczej TIMDR (2026-08-05) i jest udostępniany jako **proof-of-concept** dla eksperymentatorów, traderów koncepcyjnych oraz badaczy systemów złożonych.

---

## Filozofia działania

W trybie **lewoskrętnym (k < 0)** system:
- Opóźnia cykle temporalne (dodatnie przesunięcie fazowe)
- Wzmacnia sygnały spadkowe (asymetria)
- Generuje bardziej ostrożne rekomendacje
- Preferuje narracje ambiwalentne zamiast jednoznacznych odpowiedzi

Parametr `k` (siła skrętu) jest głównym suwakiem eksploracji – zmienia się w czasie rzeczywistym przez interfejs Streamlit.

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
- **Λ — struktura**  
  geometryczny układ skrętu, sposób ułożenia domen

- **τ — transformacja**  
  zmiana skrętu, przejście między domenami, rezonans

- **ρ — defekt**  
  odchylenie od idealnego skrętu, miara niestabilności

W tym ujęciu stabilność jest **odwrotnie proporcjonalna do defektu**:



\[
\text{lifetime} \sim \frac{1}{\rho}
\]



Minimalny defekt pojawia się na **wartościach brzegowych** —  
dyskretnej sekwencji proporcji między kolejnymi domenami.

---

## 2. Boundary Ratios (wartości brzegowe)

Model wykorzystuje prosty wzór:



\[
R_n = \frac{n^3}{(n+1)^3 - 1}
\]



To **koncepcyjna struktura**, nie prawo fizyczne.  
Służy do opisu **ciągłości skrętu** między domenami.

Przykładowe wartości:

- **8/26** — O / Fe  
- **27/63** — Co / Cu  
- **64/124** — Zn / Sb  
- **125/215** — Te / Po  

W rzeczywistych materiałach te proporcje

![Struktura brakujacych czasteczek](https://github.com/jbackk-lang/Boundary-Matter/blob/main/strukUzupel.png)

