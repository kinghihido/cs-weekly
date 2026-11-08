"""Week 03 参考实现：一次「打开网页」的时间账单。零依赖，只用标准库。

用法：
    python latency_budget.py                     # 光纤 + HTTPS + 无 CDN + 首次访问
    python latency_budget.py --net 4g --cdn      # 4G + CDN
    python latency_budget.py --cached            # 强缓存命中（回访）

它不联网，只是把讲义第 06 节那张表算出来 —— 让你看见「时间花在哪一段」。
"""

import argparse

RTT = {"fiber": 20, "4g": 40, "satellite": 600}   # 一个来回的毫秒数
RENDER = 90                                        # 解析 + 排版 + 画首屏


def budget(rtt=20, https=True, cdn=False, cached=False):
    """返回 [(阶段, 毫秒)]，顺序就是真实发生的顺序。"""
    if cached:                                     # 强缓存命中：一个字节都不用上网
        return [("读本地缓存", 2), ("解析与渲染", RENDER)]

    # CDN 省掉的是「跨城 / 跨洲」那一段，省不掉你最后一公里的链路 ——
    # 所以卫星上网（600ms 里大半是上天下地）即使有 CDN 也快不起来。
    path = min(rtt // 2, 150) if cdn else 0
    edge = rtt - path
    server = 8 if cdn else 45                      # 边缘节点比源站快
    stages = [("DNS 解析", edge), ("TCP 握手", edge)]
    if https:
        stages.append(("TLS 握手", edge))           # TLS 1.3 只要一个来回
    stages += [
        ("请求 + 首字节", edge + server),
        ("下载 HTML", 15 if cdn else 30),
        ("拉取 CSS/JS/图", 60 if cdn else 120),
        ("解析与渲染", RENDER),
    ]
    return stages


def total(stages):
    return sum(ms for _, ms in stages)


def report(stages):
    """打印一张带累计时间和条形图的账单。"""
    whole = total(stages)
    print(f"{'阶段':<16}{'本段':>7}{'累计':>8}  占比")
    print("-" * 52)
    done = 0
    for name, ms in stages:
        done += ms
        bar = "#" * max(1, round(ms / whole * 34))
        print(f"{name:<16}{ms:>5}ms{done:>7}ms  {bar} {ms / whole * 100:>4.0f}%")
    print("-" * 52)
    slowest = max(stages, key=lambda s: s[1])
    print(f"合计 {whole} ms，最重的一段是「{slowest[0]}」（{slowest[1]} ms）")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="打开一个网页要花多少毫秒")
    ap.add_argument("--net", choices=list(RTT), default="fiber", help="网络类型")
    ap.add_argument("--no-https", action="store_true", help="走 HTTP，不加密")
    ap.add_argument("--cdn", action="store_true", help="资源放在 CDN 上")
    ap.add_argument("--cached", action="store_true", help="强缓存命中（第二次访问）")
    a = ap.parse_args()

    print(f"网络：{a.net}（RTT {RTT[a.net]} ms）  HTTPS：{'否' if a.no_https else '是'}  "
          f"CDN：{'是' if a.cdn else '否'}  缓存：{'命中' if a.cached else '未命中'}\n")
    report(budget(RTT[a.net], https=not a.no_https, cdn=a.cdn, cached=a.cached))
