"""布隆过滤器（Bloom Filter）参考实现 —— 零第三方依赖。

设计要点
--------
1. 位数组用 bytearray 存，1 bit / 元素容量，内存 = m/8 字节。
2. 双哈希技巧（Kirsch-Mitzenmacher）：用两个 64 位哈希 h1、h2 生成 k 个位置
   g_i(x) = (h1 + i * h2) mod m，i = 0..k-1。理论上与 k 个独立哈希等价。
3. 参数按目标误判率自动推导，见 optimal_params()。

用法
----
    >>> bf = BloomFilter(expected_items=100_000, false_positive_rate=0.01)
    >>> bf.add("alice@example.com")
    >>> "alice@example.com" in bf
    True
    >>> "bob@example.com" in bf          # 可能 True（假阳性），但绝不会 False
"""

from __future__ import annotations

import hashlib
import math

__all__ = ["BloomFilter", "optimal_params", "theoretical_fpr"]

LN2 = math.log(2.0)


def optimal_params(n: int, p: float) -> tuple[int, int]:
    """给定预期元素数 n 与目标误判率 p，返回最优 (m, k)。

    m = -n * ln(p) / (ln2)^2
    k = (m / n) * ln2
    """
    if n <= 0:
        raise ValueError("n 必须为正整数")
    if not 0.0 < p < 1.0:
        raise ValueError("p 必须位于 (0, 1) 区间")
    m = math.ceil(-n * math.log(p) / (LN2**2))
    k = max(1, round(m / n * LN2))
    return m, k


def theoretical_fpr(m: int, k: int, n: int) -> float:
    """理论误判率：p ≈ (1 - e^(-k*n/m))^k"""
    if m <= 0 or k <= 0:
        raise ValueError("m 与 k 必须为正")
    return (1.0 - math.exp(-k * n / m)) ** k


class BloomFilter:
    """一个固定容量、只增不删的概率型集合。"""

    __slots__ = ("m", "k", "_bits", "_set_bits", "count", "_h1_salt", "_h2_salt")

    def __init__(
        self,
        expected_items: int,
        false_positive_rate: float = 0.01,
        *,
        m: int | None = None,
        k: int | None = None,
        salt: bytes = b"",
    ) -> None:
        if m is not None and k is not None:
            if m <= 0 or k <= 0:
                raise ValueError("m 与 k 必须为正")
            self.m, self.k = m, k
        else:
            self.m, self.k = optimal_params(expected_items, false_positive_rate)

        self._bits = bytearray((self.m + 7) // 8)
        self._set_bits = 0          # 已置 1 的比特数（去重后）
        self.count = 0              # 已插入的元素数（含重复插入）
        self._h1_salt = b"\x00" + salt
        self._h2_salt = b"\x01" + salt

    # ------------------------------------------------------------------ 核心
    def _positions(self, item):
        """返回该元素命中的 k 个比特位。"""
        data = item.encode("utf-8") if isinstance(item, str) else bytes(item)
        h1 = int.from_bytes(
            hashlib.blake2b(data, digest_size=8, salt=self._h1_salt).digest(), "big"
        )
        h2 = int.from_bytes(
            hashlib.blake2b(data, digest_size=8, salt=self._h2_salt).digest(), "big"
        ) | 1  # 保证与 m 互质概率更高，且避免 h2 = 0 时退化成单哈希
        return [(h1 + i * h2) % self.m for i in range(self.k)]

    def _get(self, idx: int) -> int:
        return (self._bits[idx >> 3] >> (idx & 7)) & 1

    def _set(self, idx: int) -> None:
        byte, mask = idx >> 3, 1 << (idx & 7)
        if not self._bits[byte] & mask:
            self._bits[byte] |= mask

    def add(self, item) -> bool:
        """插入元素。返回 True 表示有新比特被置位（数据被"改变"了）。"""
        changed = False
        for idx in self._positions(item):
            if not self._get(idx):
                self._set(idx)
                self._set_bits += 1
                changed = True
        self.count += 1
        return changed

    def __contains__(self, item) -> bool:
        return all(self._get(idx) for idx in self._positions(item))

    # ------------------------------------------------------------------ 观测
    @property
    def bits_set(self) -> int:
        return self._set_bits

    @property
    def load_factor(self) -> float:
        """位数组被置 1 的比例。"""
        return self._set_bits / self.m

    @property
    def memory_bytes(self) -> int:
        return len(self._bits)

    def current_fpr(self) -> float:
        """按当前实际插入量估算的误判率。"""
        return theoretical_fpr(self.m, self.k, max(self.count, 1))

    def measure_fpr(self, samples: int = 20_000, seed: int = 0) -> float:
        """用 samples 个随机串实测误判率（教学 / 测试用）。"""
        import random

        rng = random.Random(seed)
        hits = sum(
            1 for i in range(samples) if f"__probe_{rng.getrandbits(64):016x}_{i}" in self
        )
        return hits / samples

    def estimate_count(self) -> float:
        """由填充率反推元素个数：n ≈ -(m/k) * ln(1 - X/m)，X 为置位数。"""
        x = self._set_bits
        if x >= self.m:
            return float("inf")
        return -(self.m / self.k) * math.log(1.0 - x / self.m)

    def __len__(self) -> int:
        return self.count

    def __repr__(self) -> str:
        return (
            f"BloomFilter(m={self.m}, k={self.k}, n={self.count}, "
            f"fill={self.load_factor:.1%}, p≈{self.current_fpr():.4%})"
        )


if __name__ == "__main__":
    bf = BloomFilter(10_000, 0.01)
    print(bf)
    for i in range(5_000):
        bf.add(f"user:{i}")
    print(bf)
    print(f"内存占用          : {bf.memory_bytes / 1024:.1f} KiB")
    print(f"实测误判率        : {bf.measure_fpr(50_000):.4%}")
    print(f"理论误判率        : {bf.current_fpr():.4%}")
    print(f"反推元素数        : {bf.estimate_count():.0f} （真实 5000）")
