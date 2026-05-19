import unittest

from tiny_cli.cli import greet


class TinyCliTests(unittest.TestCase):
    def test_greet(self):
        self.assertEqual(greet("agent"), "hello, agent")


if __name__ == "__main__":
    unittest.main()
