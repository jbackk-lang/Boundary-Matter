# test_timdr_market.py
"""
Testy regresyjne dla TIMDRMarket (timdr_market.py).

Kazdy test odpowiada konkretnemu bledowi znalezionemu i zweryfikowanemu
w trakcie code review (patrz docstring modulu, "Historia poprawek").
Uruchomienie: pytest test_timdr_market.py -v
"""
import warnings

import numpy as np
import pytest

from timdr_market import TIMDRMarket, candles_from_ohlcv


def make_candles(close, volume, t=None):
    close = np.asarray(close, dtype=float)
    volume = np.asarray(volume, dtype=float)
    n = len(close)
    if t is None:
        t = np.arange(n, dtype=float)
    return np.column_stack([close, close, close, close, volume, t])


class TestMadZeroFallback:
    """Regresja: _mad_zscore() zwracal same zera gdy MAD=0, bez wzgledu
    na wielkosc zmiany - normalny przypadek dla sparse eventu na tle
    dlugiego spokojnego okresu (typowe dla cen/wolumenu)."""

    def test_twist_detects_obvious_price_spike(self):
        m = TIMDRMarket()
        close = np.concatenate([np.full(55, 100.0), np.linspace(100, 130, 5)])
        candles = make_candles(close, np.full(60, 1000.0))
        idx, z = m.twist_price(candles)
        assert len(idx) > 0, f"skok +30 nie wykryty, max z={np.max(z)}"

    def test_anomaly_volume_detects_obvious_spike(self):
        m = TIMDRMarket()
        close = np.full(60, 100.0)
        vol = np.full(60, 1000.0)
        vol[30] = 50000.0
        candles = make_candles(close, vol)
        idx, z = m.anomaly_volume(candles)
        assert 30 in idx, f"wolumen x50 nie wykryty, idx={idx}"

    def test_anomaly_volume_no_false_positive_on_flat(self):
        m = TIMDRMarket()
        candles = make_candles(np.full(60, 100.0), np.full(60, 1000.0))
        idx, _ = m.anomaly_volume(candles)
        assert len(idx) == 0

    def test_fallback_does_not_increase_false_positives_on_random_walk(self):
        """MAD=0 praktycznie nigdy nie wystepuje na ciaglym szumie
        cenowym - fallback nie powinien zmieniac czulosci na czysty
        random-walk bez zadnego realnego wydarzenia."""
        m = TIMDRMarket()
        rng = np.random.default_rng(7)
        false_pos = 0
        trials = 100
        for _ in range(trials):
            close = 100 + np.cumsum(rng.normal(0, 0.3, 60))
            vol = 1000 + rng.normal(0, 50, 60)
            candles = make_candles(close, vol)
            idx, _ = m.twist_price(candles)
            if len(idx) > 0:
                false_pos += 1
        # ta sama wlasciwosc progu z>3.5 co przed poprawka (~10%) - nie
        # regresja, tylko istniejaca charakterystyka progu na szumie
        assert false_pos / trials < 0.25


class TestShortSignalsDoNotCrash:
    def test_twist_price_short_signal(self):
        m = TIMDRMarket()
        for n in (0, 1, 2):
            candles = make_candles(np.arange(n), np.ones(n)) if n else np.zeros((0, 6))
            idx, z = m.twist_price(candles)
            assert len(idx) == 0

    def test_anomaly_volume_empty_no_crash(self):
        m = TIMDRMarket()
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            idx, z = m.anomaly_volume(np.zeros((0, 6)))
        assert len(idx) == 0 and len(z) == 0
        assert not any(issubclass(x.category, RuntimeWarning) for x in w)

    def test_rhythm_volume_short_signal(self):
        m = TIMDRMarket()
        for n in (0, 1, 2):
            candles = make_candles(np.arange(n), np.ones(n)) if n else np.zeros((0, 6))
            periods, score = m.rhythm_volume(candles)
            assert periods == [] and score == 0.0


class TestTrendPrice:
    """Regresja: n < window zwracalo pojedyncza tablice zamiast krotki
    (slopes, z) - kazde `slopes, z = trend_price(...)` rzucalo ValueError.
    Naprawione lepiej niz tylko zgodnym typem: krotsze okno na poczatku
    szeregu daje teraz realne (nie zerowe) oszacowanie nachylenia."""

    def test_short_history_returns_tuple_of_matching_length(self):
        m = TIMDRMarket()
        n = 10
        candles = make_candles(np.linspace(100, 110, n), np.full(n, 1000.0))
        slopes, z = m.trend_price(candles, window=20)
        assert len(slopes) == n
        assert len(z) == n

    def test_short_history_gives_real_slope_not_zeros(self):
        """n < window juz nie zwraca samych zer - kurczace sie okno
        [max(0,i-window+1):i+1] daje realne nachylenie od i=1 w gore."""
        m = TIMDRMarket()
        n = 10
        close = np.linspace(100, 110, n)  # nachylenie 10/9 na krok
        candles = make_candles(close, np.full(n, 1000.0))
        slopes, _ = m.trend_price(candles, window=20)
        assert slopes[-1] == pytest.approx(10 / 9, abs=1e-6)

    def test_recovers_known_linear_slope(self):
        m = TIMDRMarket()
        n = 40
        close = 100 + 0.5 * np.arange(n)
        candles = make_candles(close, np.full(n, 1000.0))
        slopes, _ = m.trend_price(candles, window=20)
        assert slopes[-1] == pytest.approx(0.5, abs=1e-6)

    def test_n_equals_2_no_crash(self):
        m = TIMDRMarket()
        candles = make_candles([100.0, 101.0], [1000.0, 1000.0])
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            slopes, z = m.trend_price(candles, window=20)
        assert len(slopes) == 2
        assert not any(issubclass(x.category, RuntimeWarning) for x in w)


class TestTwistPriceOnMostRecentCandle:
    """Wazne dla monitoringu na zywo: anomalia MUSI byc wykrywalna gdy
    trafia dokladnie na ostatnia (najnowsza) swiece, nie tylko gdzies
    w srodku historii."""

    def test_spike_on_last_candle_detected(self):
        m = TIMDRMarket()
        close = np.concatenate([np.full(59, 100.0), [130.0]])
        candles = make_candles(close, np.full(60, 1000.0))
        idx, z = m.twist_price(candles)
        assert len(idx) > 0
        assert z[-1] > 3.5


class TestRhythmVolume:
    def test_detects_known_period(self):
        m = TIMDRMarket()
        n = 300
        period = 20
        t = np.arange(n, dtype=float)
        vol = 1000 + 500 * np.sin(2 * np.pi * t / period)
        candles = make_candles(np.full(n, 100.0), vol, t)
        periods, score = m.rhythm_volume(candles, max_lag=60, power_thresh=0.4)
        assert period in periods


class TestCandlesFromOhlcv:
    """Adapter miedzy formatem danych tego repo (data_fetcher.py/api.py:
    slownik list) a formatem oczekiwanym przez TIMDRMarket (tablica 2D)."""

    def test_shape_and_column_mapping(self):
        ohlcv = {
            "open": [1.0, 2.0, 3.0],
            "high": [1.5, 2.5, 3.5],
            "low": [0.5, 1.5, 2.5],
            "close": [1.2, 2.2, 3.2],
            "volume": [100, 200, 300],
        }
        candles = candles_from_ohlcv(ohlcv)
        assert candles.shape == (3, 6)
        assert np.allclose(candles[:, 3], [1.2, 2.2, 3.2])   # close
        assert np.allclose(candles[:, 4], [100, 200, 300])   # volume
        assert np.allclose(candles[:, 5], [0, 1, 2])          # t (numer swiecy)

    def test_roundtrip_through_timdr_market(self):
        """Sprawdza ze adapter faktycznie dziala z klasa, nie tylko sam."""
        n = 60
        ohlcv = {
            "open": np.full(n, 100.0).tolist(),
            "high": np.full(n, 101.0).tolist(),
            "low": np.full(n, 99.0).tolist(),
            "close": np.concatenate([np.full(55, 100.0), np.linspace(100, 130, 5)]).tolist(),
            "volume": np.full(n, 1000.0).tolist(),
        }
        candles = candles_from_ohlcv(ohlcv)
        m = TIMDRMarket()
        idx, _ = m.twist_price(candles)
        assert len(idx) > 0
