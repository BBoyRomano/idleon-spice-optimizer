"""Data models for the Idleon Spice Optimizer app."""

from dataclasses import dataclass
from pathlib import Path

from constants import (
    GENETIC_ASSETS_PATH,
    MAX_TEAM_SIZE,
    SPICE_ASSETS_PATH,
    TERRITORY_ASSETS_PATH,
)
from utils import slugify


@dataclass(frozen=True)
class Genetic:
    """A trait that affects pet behavior."""

    id: int
    name: str

    @property
    def icon_path(self) -> Path:
        """Return the path to this genetic's icon image."""
        return Path(GENETIC_ASSETS_PATH) / f"{slugify(self.name)}.png"


@dataclass(frozen=True)
class Pet:
    """A foraging unit with a genetic and optional power."""

    genetic: Genetic
    power: float | None = None


@dataclass(frozen=True)
class Territory:
    """A spice-producing location with forage/fight requirements."""

    name: str
    forage: int
    fight: int

    @property
    def spice_name(self) -> str:
        """Return the name of this territory's spice."""
        return f"{self.name} Spice"

    @property
    def spice_icon_path(self) -> Path:
        """Return the path to this territory's spice icon image."""
        return Path(SPICE_ASSETS_PATH) / f"{slugify(self.spice_name)}.png"

    @property
    def background_path(self) -> Path:
        """Return the path to this territory's background image."""
        return Path(TERRITORY_ASSETS_PATH) / f"{slugify(self.name)}.png"


@dataclass(frozen=True)
class Team:
    """A group of pets assigned to a territory."""

    name: str
    pets: list[Pet]
    territory: str | None = None
    manual_speed: float | None = None

    def __post_init__(self) -> None:
        """Validate team size and pet power configuration."""
        if self.size > MAX_TEAM_SIZE:
            msg = f"A team cannot contain more than {MAX_TEAM_SIZE} pets (got {self.size})."
            raise ValueError(msg)
        if self.manual_speed is None and any(pet.power is None for pet in self.pets):
            msg = "All pets must have power if manual speed is not set."
            raise ValueError(msg)

    @property
    def size(self) -> int:
        """Return the team's size."""
        return len(self.pets)

    @property
    def speed(self) -> float:
        """Return the team's foraging speed."""
        if self.manual_speed is not None:
            return self.manual_speed
        return sum(pet.power if pet.power is not None else 0.0 for pet in self.pets)

    @property
    def genetics_counts(self) -> dict[str, int]:
        """Return the count of each genetic present in the team."""
        counts: dict[str, int] = {}
        for pet in self.pets:
            name = pet.genetic.name
            counts[name] = counts.get(name, 0) + 1
        return counts
