"""latency_budget.py 的行为测试：python test_latency_budget.py（零依赖）"""

import unittest

from latency_budget import RTT, budget, total


class TestBudget(unittest.TestCase):
    def test_total_equals_sum_of_stages(self):
        stages = budget()
        self.assertEqual(total(stages), sum(ms for _, ms in stages))

    def test_https_costs_one_round_trip(self):
        rtt = RTT["fiber"]
        self.assertEqual(total(budget(rtt, https=True)) - total(budget(rtt, https=False)), rtt)

    def test_cdn_is_faster(self):
        self.assertLess(total(budget(cdn=True)), total(budget(cdn=False)))

    def test_satellite_is_much_slower_than_fiber(self):
        self.assertGreater(total(budget(RTT["satellite"])),
                           total(budget(RTT["fiber"])) * 3)

    def test_cache_skips_the_network(self):
        names = [n for n, _ in budget(cached=True)]
        self.assertEqual(names, ["读本地缓存", "解析与渲染"])
        self.assertLess(total(budget(cached=True)), 200)

    def test_cache_makes_network_type_irrelevant(self):
        self.assertEqual(total(budget(RTT["fiber"], cached=True)),
                         total(budget(RTT["satellite"], cached=True)))

    def test_every_stage_takes_time(self):
        for name, ms in budget(RTT["satellite"], cdn=True):
            self.assertGreater(ms, 0, name)

    def test_stage_names_are_unique(self):
        names = [n for n, _ in budget()]
        self.assertEqual(len(names), len(set(names)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
