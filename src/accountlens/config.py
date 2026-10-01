"""Shared project configuration."""

from __future__ import annotations

import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Load project-local settings before evaluating module-level configuration.
# Environment variables already set by the operating system keep precedence.
try:
    from dotenv import load_dotenv

    load_dotenv(PROJECT_ROOT / ".env", override=False)
except ImportError:
    pass

DEFAULT_DATA_DIR = PROJECT_ROOT / "data" / "generated"
DEFAULT_RESULTS_DIR = PROJECT_ROOT / "results"
DEFAULT_LOG_DIR = PROJECT_ROOT / "logs"
DEFAULT_PROMPT_PATH = PROJECT_ROOT / "prompts" / "account_briefing_v2.txt"
M1_PROMPT_PATH = PROJECT_ROOT / "prompts" / "account_briefing_m1.txt"
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-2024-11-20")
DEFAULT_ABSTENTION_THRESHOLD = float(os.getenv("ACCOUNTLENS_ABSTENTION_THRESHOLD", "0.65"))

# Pricing assumptions for the pinned GPT-4o model. These values are metadata,
# not billing guarantees; update them before the final experiment if prices change.
INPUT_COST_PER_MILLION_USD = 2.50
OUTPUT_COST_PER_MILLION_USD = 10.00
MAX_OUTPUT_TOKENS = 2_000
