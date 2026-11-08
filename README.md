# 每周一个计算机小知识 · CS Weekly

> 给**爱好者**的计算机常识课：不懂算法没关系，会开机就能读。
> 每周一期：讲清一个「天天在用但说不明白」的东西 + 一个动手小挑战。

🔗 在线讲义：<https://kinghihido.github.io/cs-weekly/>

---

## 定位（重要）

这不是程序员培训，也不打算教你刷题。

- ✅ 讲硬件怎么分工、软件为什么这么设计、电脑坏了怎么判断
- ✅ 每期都有能在浏览器里点的小演示，看完就有体感
- ✅ 挑战以「观察 + 10 行以内代码」为主，零基础能做
- ❌ 不推导复杂数学，不要求手写算法 —— 那些交给 AI

**为什么还值得学？** 因为 AI 能替你写代码，但替不了你「把问题说清楚」。
懂结构、会看资源在哪儿排队、能读懂报错最后一行 —— 这三件事决定你用 AI 的效率。

## 期数索引

| # | 主题 | 一句话 | 讲义 | 挑战 |
| --- | --- | --- | --- | --- |
| 01 | 你的代码是怎么跑起来的 | CPU / 内存 / 硬盘怎么分工，一行 `print` 走完六站 | [week-01](week-01/README.md) | [Lv1-3](week-01/CHALLENGE.md) |
| 02 | 你的密码，网站到底怎么存的 | 指纹（哈希）、加盐、慢哈希，以及为什么网站只能让你「重置密码」 | [week-02](week-02/README.md) | [Lv1-3](week-02/CHALLENGE.md) |
| 03 | 一个网址，从按下回车到看见页面 | DNS / 握手 / HTTP / CDN / 渲染，把打开网页的 0.4 秒拆成五段 | [week-03](week-03/README.md) | [Lv1-3](week-03/CHALLENGE.md) |

后续候选：SSD 为什么快、程序为什么会崩、操作系统到底在干什么。
想听哪个，开 Issue 投票。

## 快速开始

```bash
git clone https://github.com/kinghihido/cs-weekly.git
cd cs-weekly
```

本期讲义有两种读法：

1. **直接看网页**：双击 `index.html`（内含三个可点击的小演示，不需要联网、不需要服务器，所有计算在浏览器本地完成）。
2. **看 Markdown 版**：[`week-03/README.md`](week-03/README.md)。

## 本期速览（Week 03）

| 概念 | 一句话记住 |
| --- | --- |
| DNS | 名字是给人用的稳定入口，IP 是给机器用的临时坐标；路上每一层都在缓存，所以「生效慢」是在等缓存过期 |
| 握手 | TCP 一个来回建路，TLS 一个回车上锁；慢的大头是「来回几次」，不是「数据多少」 |
| 光速极限 | 光纤 RTT 20ms ≈ 服务器在 2000 公里外；跨太平洋一个来回 100ms，谁也修不了 |
| HTTP | 4 开头是你的问题，5 开头是它的问题；「登录状态」只是一张每次都要出示的 Cookie |
| CDN | 省的是「跨城跨洲」，省不掉「最后一公里」；效果全看命中率 |
| 渲染 | HTML 只是施工图，CSS/JS/图是之后分批取的材料；普通 `<script>` 会挡住解析 |
| 缓存 | 缓存不是让事情变快，是让大部分事情根本不用发生 |

**核心句（唯一需要记的一行）**：慢的大头往往不是「数据有多少」，而是「要来回几次」 —— 所以白屏要分段查，不要整体骂。

本地跑参考实现（零依赖）：

```bash
cd week-03
python latency_budget.py                # 亲眼看：一次访问的时间账单
python latency_budget.py --net satellite --cdn
python test_latency_budget.py           # 8 个行为测试
```

## 参与

- 讲错了、说不明白：直接开 Issue，欢迎打脸。
- 完成挑战：开 Issue 打卡（标题「Week02 打卡」，以此类推），贴观察或数字就行。
- 提主题：开 Issue 说「我想搞懂 XX」，附一句你为什么好奇。

## 目录约定

```
cs-weekly/
├── index.html              # 当期交互讲义（GitHub Pages 入口）
├── week-01/
│   ├── index.html          # 第 01 期交互讲义（存档）
│   ├── README.md           # 讲义正文（Markdown 版）
│   ├── CHALLENGE.md        # 本周挑战
│   └── submissions/        # 挑战提交（可选）
├── week-02/
│   ├── index.html          # 第 02 期交互讲义（存档）
│   ├── README.md           # 第 02 期讲义（密码是怎么存的）
│   ├── CHALLENGE.md
│   ├── salt_demo.py
│   ├── test_salt_demo.py
│   └── submissions/
├── week-03/
│   ├── README.md           # 第 03 期讲义（网址从输入到出现）
│   ├── CHALLENGE.md        # 本周挑战（网速分段体检）
│   ├── latency_budget.py   # 时间账单参考实现（零依赖）
│   ├── test_latency_budget.py
│   └── submissions/
├── archive/
│   └── bloom-filter/       # 旧版第 01 期（布隆过滤器，技术向，留档）
└── week-NN/ ...            # 后续期数
```

## License

文字 CC BY 4.0，代码 MIT。转载署名即可。
