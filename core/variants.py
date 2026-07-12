"""
Генерация похожих вариантов никнейма.

По базовому нику строит правдоподобные варианты
(регистр, разделители, суффиксы, приставки), которыми
затем опрашиваются сервисы.
"""

from __future__ import annotations

import re

# Суффиксы-годы и числа, которые часто добавляют к никам.
_NUMERIC_SUFFIXES = ("1", "01", "123", "2024", "2025", "2026")

# Текстовые приставки/суффиксы (реальные паттерны из промпта).
_PREFIXES = ("real", "the", "official", "its", "im")
_SUFFIXES = (
    "official",
    "real",
    "dev",
    "tv",
    "live",
    "yt",
    "hq",
    "x",
)

# Разделители, через которые «склеивают» составные ники.
_SEPARATORS = ("_", "-", ".")


def _clean(username: str) -> str:
    """Убрать пробелы по краям."""
    return username.strip()


def _split_words(username: str) -> list[str]:
    """
    Разбить ник на слова по разделителям и camelCase,
    чтобы уметь строить nick_name / nick-name из nickname.
    """
    parts = re.split(r"[_\-.\s]+", username)
    parts = [p for p in parts if p]

    if len(parts) == 1:
        # camelCase / PascalCase -> ["nick", "Name"]
        camel = re.findall(
            r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+|\d+",
            username,
        )
        if len(camel) > 1:
            parts = camel

    return parts


def generate_variants(
    username: str,
    include_similar: bool = True,
    limit: int | None = None,
) -> list[str]:
    """
    Построить список вариантов ника.

    :param username: исходный ник.
    :param include_similar: добавлять ли похожие варианты
        (иначе вернётся только очищенный оригинал).
    :param limit: ограничение на количество вариантов.
    :return: отсортированный список уникальных вариантов,
        оригинал всегда первый.
    """
    original = _clean(username)

    if not original:
        return []

    if not include_similar:
        return [original]

    variants: set[str] = {
        original,
        original.lower(),
        original.upper(),
        original.capitalize(),
    }

    base = original.lower()

    # Числовые суффиксы: nickname1, nickname2025 ...
    for suffix in _NUMERIC_SUFFIXES:
        variants.add(f"{base}{suffix}")

    # Текстовые суффиксы/приставки: realnickname, nickname_official ...
    for pre in _PREFIXES:
        variants.add(f"{pre}{base}")
        variants.add(f"{pre}_{base}")

    for suf in _SUFFIXES:
        variants.add(f"{base}{suf}")
        variants.add(f"{base}_{suf}")

    # Замена разделителей для составных ников: nick_name <-> nick-name
    words = _split_words(original)
    if len(words) > 1:
        low_words = [w.lower() for w in words]
        for sep in _SEPARATORS:
            variants.add(sep.join(low_words))
        variants.add("".join(low_words))

    # Оригинал всегда идёт первым, остальное — по алфавиту.
    rest = sorted(v for v in variants if v != original)
    ordered = [original] + rest

    if limit is not None:
        ordered = ordered[:limit]

    return ordered
