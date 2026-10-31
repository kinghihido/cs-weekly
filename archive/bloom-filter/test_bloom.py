"""布隆过滤器测试：python -m pytest week-01/test_bloom.py -v （或直接 python 运行）"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from bloom import BloomFilter, optimal_params, theoretical_fpr  # noqa: E402


def test_no_false_negative():
    """核心承诺：已插入的元素必须 100% 命中。"""
    bf = BloomFilter(expected_items=1_000, false_positive_rate=0.01)
    items = [f"item-{i}" for i in range(1_000)]
    for it in items:
        bf.add(it)
    missing = [it for it in items if it not in bf]
    assert not missing, f"出现假阴性，这是实现 bug：{missing[:5]}"


def test_optimal_params_match_theory():
    m, k = optimal_params(10_000, 0.01)
    # 教科书数值：约 9.6 bit/元素，k ≈ 7
    assert abs(m / 10_000 - 9.585) < 0.05
    assert k == 7


def test_fpr_close_to_theory():
    """m、k 由公式推导时，实测误判率应与理论值同量级。"""
    bf = BloomFilter(expected_items=5_000, false_positive_rate=0.01)
    for i in range(5_000):
        bf.add(f"u{i}")
    measured = bf.measure_fpr(samples=50_000, seed=42)
    theory = bf.current_fpr()
    assert 0.5 * theory < measured < 2.0 * theory, (measured, theory)


def test_fpr_rises_with_overfill():
    """塞入远超设计容量的元素，误判率必然上升。"""
    bf = BloomFilter(expected_items=200, false_positive_rate=0.01)
    early = bf.current_fpr()
    for i in range(2_000):
        bf.add(f"x{i}")
    assert bf.current_fpr() > early * 5


def test_empty_filter_has_no_false_positive():
    bf = BloomFilter(expected_items=100)
    assert "anything" not in bf
    assert bf.bits_set == 0


def test_memory_is_compact():
    """100 万元素、1% 误判率，应约 1.2 MB 而非 100 MB。"""
    bf = BloomFilter(expected_items=1_000_000, false_positive_rate=0.01)
    assert bf.memory_bytes < 1_300_000
    assert bf.memory_bytes > 1_000_000


def test_estimate_count():
    bf = BloomFilter(expected_items=1_000, false_positive_rate=0.01)
    for i in range(1_000):
        bf.add(f"z{i}")
    assert abs(bf.estimate_count() - 1_000) < 100


def test_add_reports_new_bits():
    bf = BloomFilter(expected_items=100)
    assert bf.add("a") is True
    assert bf.add("a") is False  # 重复插入不再改变位数组


def test_theoretical_fpr_monotonic_in_k():
    """固定 m/n 时，误判率随 k 先降后升，存在最优 k。"""
    m, n = 10_000, 1_000
    vals = [theoretical_fpr(m, k, n) for k in range(1, 13)]
    best = vals.index(min(vals)) + 1
    assert best == round(m / n * math.log(2))


if __name__ == "__main__":
    failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"  PASS  {name}")
            except AssertionError as exc:
                failed += 1
                print(f"  FAIL  {name}  -> {exc}")
    print(f"\n{'全部通过' if failed == 0 else str(failed) + ' 个失败'}")
    sys.exit(1 if failed else 0)
