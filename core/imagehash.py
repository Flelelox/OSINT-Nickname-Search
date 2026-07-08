"""
Перцептивное хэширование изображений (dHash).

Позволяет сравнивать аватары разных аккаунтов: если хэши
близки (малое расстояние Хэмминга) — картинки похожи, что
повышает вероятность принадлежности одному человеку.
"""

from __future__ import annotations

from io import BytesIO

try:
    from PIL import Image
    _PIL_OK = True
except Exception:  # pragma: no cover - pillow должен быть установлен
    _PIL_OK = False


def dhash(data: bytes, size: int = 8) -> str | None:
    """
    Difference hash изображения -> hex-строка.
    Возвращает None, если картинку не удалось прочитать.
    """
    if not _PIL_OK or not data:
        return None

    try:
        image = (
            Image.open(BytesIO(data))
            .convert("L")
            .resize((size + 1, size))
        )
    except Exception:
        return None

    pixels = image.load()

    bits = []
    for y in range(size):
        for x in range(size):
            bits.append("1" if pixels[x, y] < pixels[x + 1, y] else "0")

    value = int("".join(bits), 2)
    width = size * size // 4  # длина hex-строки

    return f"{value:0{width}x}"


def hamming(a: str | None, b: str | None) -> int:
    """
    Расстояние Хэмминга между двумя hex-хэшами.
    Большое число (999) означает «несравнимо».
    """
    if not a or not b or len(a) != len(b):
        return 999

    try:
        return bin(int(a, 16) ^ int(b, 16)).count("1")
    except ValueError:
        return 999


def similar(a: str | None, b: str | None, threshold: int = 10) -> bool:
    """True, если два аватара достаточно похожи."""
    return hamming(a, b) <= threshold
