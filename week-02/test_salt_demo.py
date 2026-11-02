"""test_salt_demo.py —— 验证参考实现的行为，顺便当「可执行文档」读

运行：python test_salt_demo.py      （只用标准库 unittest）
"""

import unittest

from salt_demo import fingerprint, login, new_salt, register


class TestFingerprint(unittest.TestCase):
    def test_长度固定(self):
        for text in ["", "a", "x" * 1000, "中文密码"]:
            self.assertEqual(len(fingerprint(text)), 64)

    def test_已知答案(self):
        # 和网页版、以及 `echo -n | sha256sum` 的结果一致，可互相校验
        self.assertEqual(
            fingerprint("hunter2"),
            "f52fbd32b2b3b86ff88ef6c490628285f482af15ddcb29541f94bcf526a3f6c7",
        )
        self.assertEqual(
            fingerprint(""),
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        )

    def test_雪崩效应(self):
        a, b = fingerprint("hunter2"), fingerprint("hunter3")
        changed = sum(1 for x, y in zip(a, b) if x != y)
        self.assertGreater(changed, 40, "改一个字符，应有大半个指纹变化")


class TestSalt(unittest.TestCase):
    def test_盐每次都不同(self):
        self.assertNotEqual(new_salt(), new_salt())
        self.assertEqual(len(new_salt()), 16)

    def test_同一密码两次注册指纹不同(self):
        _, h1 = register("iloveyou123")
        _, h2 = register("iloveyou123")
        self.assertNotEqual(h1, h2)

    def test_不加盐则指纹相同(self):
        # 这是反例：没有盐时，同一密码在所有用户那里长得一模一样
        self.assertEqual(fingerprint("123456"), fingerprint("123456"))


class TestLogin(unittest.TestCase):
    def test_正确密码通过(self):
        salt, stored = register("咖啡凉了才想起减肥")
        self.assertTrue(login("咖啡凉了才想起减肥", salt, stored))

    def test_错误密码被拒(self):
        salt, stored = register("咖啡凉了才想起减肥")
        self.assertFalse(login("咖啡凉了才想起减肥 ", salt, stored))   # 多一个空格也不行

    def test_库里没有明文密码(self):
        pw = "iloveyou123"
        salt, stored = register(pw)
        self.assertNotIn(pw, salt + stored)


if __name__ == "__main__":
    unittest.main(verbosity=2)
