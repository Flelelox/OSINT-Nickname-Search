"""
Алгоритмы вычисления процента совпадения никнеймов.

Используются несколько метрик, результат — их взвешенная оценка:
- SequenceMatcher (difflib)
- Levenshtein (rapidfuzz.fuzz.ratio)
- Jaro-Winkler
- Damerau-Levenshtein
- N-граммы (коэффициент Дайса)
"""

from __future__ import annotations

from difflib import SequenceMatcher

from rapidfuzz import fuzz
from rapidfuzz.distance import JaroWinkler, DamerauLevenshtein

from core.variants import generate_variants


class Similarity:

    # =====================================================
    # Отдельные метрики (все возвращают 0..100)
    # =====================================================

    @staticmethod
    def sequence(a: str, b: str) -> float:
        return round(
            SequenceMatcher(None, a.lower(), b.lower()).ratio() * 100,
            2,
        )

    @staticmethod
    def levenshtein(a: str, b: str) -> float:
        return float(fuzz.ratio(a.lower(), b.lower()))

    @staticmethod
    def partial(a: str, b: str) -> float:
        return float(fuzz.partial_ratio(a.lower(), b.lower()))

    @staticmethod
    def token_sort(a: str, b: str) -> float:
        return float(fuzz.token_sort_ratio(a.lower(), b.lower()))

    @staticmethod
    def jaro_winkler(a: str, b: str) -> float:
        return round(
            JaroWinkler.normalized_similarity(a.lower(), b.lower()) * 100,
            2,
        )

    @staticmethod
    def damerau(a: str, b: str) -> float:
        return round(
            DamerauLevenshtein.normalized_similarity(a.lower(), b.lower()) * 100,
            2,
        )

    @staticmethod
    def ngram(a: str, b: str, n: int = 2) -> float:
        """
        Похожесть по n-граммам (коэффициент Сёренсена-Дайса).
        """
        a = a.lower()
        b = b.lower()

        if a == b:
            return 100.0

        if len(a) < n or len(b) < n:
            return Similarity.sequence(a, b)

        grams_a = {a[i:i + n] for i in range(len(a) - n + 1)}
        grams_b = {b[i:i + n] for i in range(len(b) - n + 1)}

        if not grams_a or not grams_b:
            return 0.0

        overlap = len(grams_a & grams_b)

        return round(
            2 * overlap / (len(grams_a) + len(grams_b)) * 100,
            2,
        )

    # =====================================================
    # Итоговая взвешенная оценка
    # =====================================================

    @staticmethod
    def score(a: str, b: str) -> float:
        """
        Взвешенная оценка похожести двух ников (0..100).
        Jaro-Winkler и Levenshtein весят больше как наиболее
        подходящие для коротких строк-идентификаторов.
        """
        if not a or not b:
            return 0.0

        weighted = [
            (Similarity.jaro_winkler(a, b), 0.30),
            (Similarity.levenshtein(a, b), 0.25),
            (Similarity.damerau(a, b), 0.20),
            (Similarity.sequence(a, b), 0.15),
            (Similarity.ngram(a, b), 0.10),
        ]

        total = sum(value * weight for value, weight in weighted)

        return round(total, 2)

    # =====================================================
    # Генерация вариантов (совместимость; логика в core.variants)
    # =====================================================

    @staticmethod
    def generate(username: str) -> list[str]:
        return generate_variants(username)
