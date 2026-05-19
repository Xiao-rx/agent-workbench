from __future__ import annotations


def greet(name: str) -> str:
    return f"hello, {name}"


def main() -> int:
    print(greet("agent"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
