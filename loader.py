"""Data loading functions for the Idleon Spice Optimizer app."""

import json
from pathlib import Path
from typing import Any, TypeVar

import streamlit as st

from models import Genetic, Territory

T = TypeVar("T")

DATA_DIR = Path("data")
TERRITORIES_JSON = DATA_DIR / "territories.json"
GENETICS_JSON = DATA_DIR / "genetics.json"


@st.cache_data
def load_json(path: Path) -> list[dict[str, Any]]:
    """Load raw JSON content from a file."""
    with Path.open(path, encoding="utf-8") as f:
        return json.load(f)


def load_items(path: Path, model: type[T]) -> list[T]:
    """Deserialize a list of dicts into a list of dataclass instances."""
    return [model(**entry) for entry in load_json(path)]


@st.cache_data
def load_territories(path: Path = TERRITORIES_JSON) -> list[Territory]:
    """Load all territory definitions from disk."""
    return load_items(path, Territory)


@st.cache_data
def load_genetics(path: Path = GENETICS_JSON) -> list[Genetic]:
    """Load all genetics definitions from disk."""
    return load_items(path, Genetic)


@st.cache_data
def build_genetics_by_id(genetics: list[Genetic]) -> dict[int, Genetic]:
    """Build a lookup table for genetics by ID."""
    return {g.id: g for g in genetics}


@st.cache_data
def build_genetics_by_name(genetics: list[Genetic]) -> dict[str, Genetic]:
    """Build a lookup table for genetics by name."""
    return {g.name: g for g in genetics}


@st.cache_data
def build_territories_by_name(territories: list[Territory]) -> dict[str, Territory]:
    """Build a lookup table for territories by name."""
    return {t.name: t for t in territories}
