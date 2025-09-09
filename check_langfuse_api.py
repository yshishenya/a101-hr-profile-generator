#!/usr/bin/env python3
"""
Проверка доступных методов Langfuse API
"""

import os
import sys
from pathlib import Path

# Загрузка .env переменных
env_path = Path("/home/yan/A101/HR/.env")
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key] = value

from langfuse import Langfuse


def check_langfuse_methods():
    """Проверяем доступные методы Langfuse"""

    langfuse = Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_HOST"),
    )

    print("📋 Available Langfuse methods:")
    methods = [method for method in dir(langfuse) if not method.startswith("_")]

    trace_methods = [m for m in methods if "trace" in m.lower()]
    generation_methods = [m for m in methods if "generation" in m.lower()]

    print(f"\n🔗 Trace-related methods:")
    for method in trace_methods:
        print(f"  - {method}")

    print(f"\n🤖 Generation-related methods:")
    for method in generation_methods:
        print(f"  - {method}")

    print(f"\n📝 All methods:")
    for method in sorted(methods):
        print(f"  - {method}")


if __name__ == "__main__":
    check_langfuse_methods()
