# Boundary‑Matter  
### Geometry • Twist • Stability

Materia nie jest zbiorem pierwiastków.  
Materia jest **strukturą skrętu**, a jej stabilność wynika z **wartości brzegowych** między kolejnymi domenami geometrycznymi.

Ten projekt dokumentuje model Λ–τ–ρ oraz jego zastosowanie do realnych materiałów.

---

## 1. Model Λ–τ–ρ

- **Λ — struktura** (geometryczny układ skrętu)  
- **τ — transformacja** (zmiana skrętu, rezonans, przejście domeny)  
- **ρ — defekt** (odchylenie od idealnego skrętu)

Stabilność materii jest odwrotnie proporcjonalna do defektu:



\[
\text{lifetime} \sim \frac{1}{\rho}
\]



Minimalne ρ pojawia się na **wartościach brzegowych**:



\[
\frac{n^3}{(n+1)^3 - 1}
\]



---

## 2. Boundary Ratios

Te dyskretne proporcje pojawiają się w realnych materiałach:

| Ratio | Interpretation | Candidate Elements | Notes |
|------|----------------|-------------------|-------|
| 8 / 26 | \(2^3 / (3^3 - 1)\) | O / Fe | YIG, ferrimagnetic time crystal |
| 27 / 63 | \(3^3 / (4^3 - 1)\) | Co / Cu | topological metals |
| 64 / 124 | \(4^3 / (5^3 - 1)\) | Zn / Sb | topological insulators |
| 125 / 215 | \(5^3 / (6^3 - 1)\) | Te / Po | strong spin–orbit coupling |

Każdy z tych układów wykazuje **anomalia stabilności**, rezonanse spinowe lub zachowania topologiczne.

---

## 3. Why these ratios are not coincidences

Różne klasy materiałów — ferrimagnety, metale, izolatory topologiczne, układy spin–orbita — trafiają w te same proporcje.

To nie jest przypadek.  
To jest **ciągłość skrętu** między kolejnymi domenami:



\[
2^3 \rightarrow 3^3 \rightarrow 4^3 \rightarrow 5^3
\]



Każda domena ma swoją wartość brzegową, a materia „wybiera” te punkty, bo minimalizują defekt ρ.

---

## 4. Experimental Sketch: Co/Cu (27/63)

Proponowany eksperyment testujący stabilność cyklicznych stanów spinowych.

**Cel:**  
Sprawdzić, czy multilayer Co/Cu o stosunku 27:63 wykazuje podharmoniczne oscylacje (czas‑krystaliczne) pod okresowym napędem.

**Układ:**

- Co(t₁) / Cu(t₂) powtarzane N razy  
- grubości dobrane tak, by Co:Cu ≈ 27:63  
- podłoże: Si/SiO₂

**Pobudzenie:**

- pole statyczne \(B_0\)  
- napęd mikrofalowy (GHz) o okresie T  

**Pomiary:**

- GMR w funkcji czasu  
- FMR/ESR  
- szukanie odpowiedzi 2T, 3T, … przy napędzie T

**Hipoteza Boundary‑Matter:**  
Na stosunku 27/63 defekt ρ jest minimalny → czas życia stanów cyklicznych jest maksymalny dla tego materiału.

---

## 5. Rezonans w metalurgii (real‑world analogy)

Procesy hutnicze zawierają ukryte rezonanse:

- **elektromagnetyczne** (piece indukcyjne),  
- **akustyczne** (pulsacje komory),  
- **hydrodynamiczne** (fale ciekłego metalu).

To naturalne środowiska skrętu τ i defektu ρ — dlatego materia krystalizuje w dyskretnych domenach.

---

## 6. Boundary‑Matter Summary

- materia = skręt, nie chemia  
- stabilność = minimalny defekt ρ  
- defekt minimalny na wartościach brzegowych  
- te wartości pojawiają się w realnych materiałach  
- można je testować eksperymentalnie (Co/Cu, Zn/Sb, YIG)

---

## 7. Diagram

![Boundary Ratio Table](diagrams/boundary_ratio_table.png)

---

## 8. License

MIT
