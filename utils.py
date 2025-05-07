"""Utility functions for the Idleon SPice Optimizer app."""

import base64
import re
from pathlib import Path

import streamlit as st


def slugify(string: str) -> str:
    """Convert a string into a slugified, filename-safe format."""
    return re.sub(r"[^a-zA-Z0-9_]", "", string.replace(" ", "_"))


@st.cache_data
def image_to_base64_uri(path: Path) -> str:
    """Return a base64-encoded data URI from an image file."""
    encoded = base64.b64encode(path.read_bytes()).decode()
    return f"data:image/png;base64,{encoded}"


def format_time(hours: float) -> str:
    """Convert float hours into 'Xh Ym', 'Ym Zs', or 'Zs' format."""
    total_seconds = round(hours * 3600)
    h, remainder = divmod(total_seconds, 3600)
    m, s = divmod(remainder, 60)

    if h:
        return f"{h}h {m}m" if m else f"{h}h"
    if m:
        return f"{m}m {s}s" if s else f"{m}m"

    return f"{s}s" if s else "0s"


def format_number(number: float) -> str:
    """Return a float formatted in Idleon-style compact notation."""
    thresholds: list[tuple[float, str | None]] = [
        (1e24, None),
        (1e21, "QQQ"),
        (1e18, "QQ"),
        (1e15, "Q"),
        (1e12, "T"),
        (1e9,  "B"),
        (1e6,  "M"),
        (1e3,  "K"),
    ]

    for threshold, suffix in thresholds:
        if number >= threshold:
            return f"{number / threshold:.2f}{suffix}" if suffix else f"{number:.2E}"

    return f"{int(number)}"
