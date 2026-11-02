"""salt_demo.py —— 30 行看懂「网站到底存了你什么」

这是第 02 期的参考实现，只用 Python 自带的库，不需要 pip install。

三个函数就是全部真相：
  fingerprint()  把任意文字压成一串 64 位的「指纹」（哈希），单向、不可逆
  new_salt()     每个账号一份随机盐
  register()     注册时：造盐 → 算指纹 → 存「盐 + 指纹」（不存密码）
  login()        登录时：拿你的输入 + 库里的盐重算一遍，和存的指纹比

⚠️ 一句话提醒：真实项目请用 bcrypt / argon2，不要用 sha256 存密码。
   原因见讲义第 04 节：SHA-256 算得太快，攻击者每秒能试几十亿次。
   这里的 sha256 只是为了让代码短到你能一眼看完。
"""

import hashlib
import secrets


def fingerprint(text: str) -> str:
    """把任意长度的文字压成固定 64 个字符的指纹。改一个字，整串全变，且无法反推。"""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def new_salt() -> str:
    """随机盐。盐不需要保密，和指纹一起明文存在数据库里就行。"""
    return secrets.token_hex(8)          # 8 字节 → 16 个十六进制字符


def register(password: str) -> tuple[str, str]:
    """返回网站真正存下的两样东西：盐 + 指纹。注意：密码本身没有留下。"""
    salt = new_salt()
    return salt, fingerprint(salt + password)


def login(password: str, salt: str, stored: str) -> bool:
    """把用户这次输入重新算一遍，和库里存的比。一样就是本人。"""
    return fingerprint(salt + password) == stored


if __name__ == "__main__":
    pw = "iloveyou123"

    # ① 同一个密码，注册两次，两次的指纹完全不同 —— 因为有盐
    s1, h1 = register(pw)
    s2, h2 = register(pw)
    print("第一次注册  盐:", s1, " 指纹:", h1)
    print("第二次注册  盐:", s2, " 指纹:", h2)
    print("同一密码指纹相同吗？", h1 == h2, "  ← 应该 False\n")

    # ② 登录校验：密码对了就通过
    print("用正确密码登录：", login(pw, s1, h1), "  ← 应该 True")
    print("用错误密码登录：", login(pw + "x", s1, h1), "  ← 应该 False\n")

    # ③ 雪崩效应：只改最后一个字符，指纹变得面目全非
    a, b = fingerprint("hunter2"), fingerprint("hunter3")
    diff = sum(1 for x, y in zip(a, b) if x != y)
    print("hunter2 →", a)
    print("hunter3 →", b)
    print(f"64 个字符里有 {diff} 个变了\n")

    # ④ 自己查一遍「第一页字典」：如果你的密码在这张表里，等于没设
    for weak in ["123456", "password", "qwerty", "5201314"]:
        print(f"{weak:12s} 的指纹 = {fingerprint(weak)[:16]}…")
