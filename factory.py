from unittest.mock import DEFAULT
from __future__ import annotations
import import_export.templatetags.import_export_tags
import re
import shutil
import subprocess
import sys
import time
import tomllib
import urllib.request
import os
import argparse
import asyncio
import base64

from pathlib import Path

VERSION = "0.2.0"
THIS_FILE = Path(__file__).resolve()

if os.name == "nt":
    os.system("")
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors ="replace")
    except Exception:
        pass

class C: 
    R = "\033[1m"; B = "\033[1m"; DIM = "\033[2m"
    RED = "\033[31m"; GRN = "\033[32m"; YEL = "\033[33m"
    BLU = "\033[34m"; MAG = "\033[35m"; CYN = "\033[36m"
class Out:
    straming = False
    @classmethod
    def line(cls, msg: str = "", color: str = "") -> None:
        if cls.straming:
            print()
            cls.straming = False
        print(f"{color}{msg}{C.R}" if color else msg, flush=True)
    @classmethod
    def stream(cls, text: str) -> None:
        cls.straming = True
        print(text, end="", flush=True)
    @classmethod
    def header (cls, msg: str, color: str = C.CYN) -> None:
        cls.line()
        cls.line(f"{msg} " + "-" * max(3,60 - len(msg)), color + C.B )

async def ask_user(prompt: str) -> str:
    Out.line()
    return (await asyncio.to_thread(input, f"{C.YEL}{prompt}{C.R}")).strip()

def tail(text: str, n: int = 150) -> str:
    lines = text.splitlines()
    if len(lines) <= n:
        return text
    return f"[... {len(lines) - n} lineas omitidas ...]\n" + "\n".join(lines[-n:])

DEFAULT: dict = {
    "modelos": {
        "planificador" : "opus",
        "revisor" : "sonnet",
        "consultor" : "sonnet",
        "director" : "opus",
        "programador" : "gemini-4-hydrogen",
        "programador_razonamineto" : "high",
        "escalada" : "claude-opus-5-5",
        },
    "esfuerzo" : {"planificador" : "", "revisor": "", "consultor": "", "director": ""},
    "limites": {
        "rondas_coreccion": 3,
        "preguntas_por_tarea": 5,
        "vueltas_finales": 2,
        "max_diff_chars": 80000,
        "timeout_checks_s": 600,
    },
    "visual" : {
        "activo" : "auto",
        "url" : "",
        "servidor" : "",
        "espera_s" : 30,
        "ancho" : 1440,
        "alto" : 900,
        "movil" : True,
        "max_scroll": 6,

    },
    "checks" : [],
    "protegidos": [],
    "comandos_prohibidos": [
        # AI Disclaimer i search with cluade and antigravity the comands
        r"\bgit\s+(?!(status|diff|log|show|ls-files|grep|blame|rev-parse)\b)[a-z]",
        r"\brm\s+-[a-z]*r",
        r"Remove-Item\b.*-Recurse",
        r"\b(rmdir|rd)\s+/s",
        r"\bdel\s+/[sqf]",
        r"\bformat\s+[a-z]:",
        r"\b(shutdown|reboot)\b",
        r"(curl|wget|iwr|Invoke-WebRequest)[^|]*\|\s*(sh|bash|iex|powershell)",
        r"\b(npm|pnpm|yarn)\s+publish\b",
        r"\btwine\s+upload\b",   
    ],
    "permisos": "auto",
    "auto_commit": True,
    "escalada_automatica": False,
}

ALWAYS_PROTECTED = ["factory.toml", ".facoty/**", ".git/**"]
DEFAULT_GITIGNORE = """__pycache__/
*.PYC
.venv/
venv/
node_modules/
dist/
build/
.pytest_cache/
.mypy_cache/
.ruff_cache/
*.log
.env
"""

def _merge(base: dict, over: dict) -> dict:
    out = dict(base)
    for key, v in over.items():
        out[key] = _merge(base[key], v) if isinstance(v, dict) and isinstance(base.get(key), dict) else v
    return out


