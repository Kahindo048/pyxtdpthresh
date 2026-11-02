"""Pure Python MT19937-64, written from the reference C code with unbounded integers."""

from __future__ import annotations

_MASK = (1 << 64) - 1
_MATRIX_A = 0xB5026F5AA96619E9
_UPPER = 0xFFFFFFFF80000000
_LOWER = 0x7FFFFFFF


class MT64:
    """Reference generator: ``MT64(seed).next()`` gives successive 64-bit outputs."""

    def __init__(self, seed: int) -> None:
        self.mt = [0] * 312
        self.mt[0] = seed & _MASK
        for i in range(1, 312):
            prev = self.mt[i - 1]
            self.mt[i] = (6364136223846793005 * (prev ^ (prev >> 62)) + i) & _MASK
        self.index = 312

    def _twist(self) -> None:
        mt = self.mt
        for i in range(312):
            x = (mt[i] & _UPPER) | (mt[(i + 1) % 312] & _LOWER)
            mt[i] = mt[(i + 156) % 312] ^ (x >> 1) ^ (_MATRIX_A if x & 1 else 0)
        self.index = 0

    def next(self) -> int:
        """Next tempered 64-bit output."""
        if self.index >= 312:
            self._twist()
        x = self.mt[self.index]
        self.index += 1
        x ^= (x >> 29) & 0x5555555555555555
        x ^= (x << 17) & 0x71D67FFFEDA60000
        x ^= (x << 37) & 0xFFF7EEE000000000
        x ^= x >> 43
        return x & _MASK
