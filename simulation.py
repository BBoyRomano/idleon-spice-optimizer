"""Run spice simulation logic for the Idleon Spice Optimizer app."""

from typing import Iterator, Optional

from models import Team, Territory

ALCHEMIC = "Alchemic"
MONOLITHIC = "Monolithic"


def count_genetic(team: Team, name: str) -> int:
    """Return the number of pets on the team with a given genetic name."""
    return sum(1 for pet in team.pets if pet.genetic.name == name)


def calculate_forage_requirement(
    base: float,
    fills: int,
    monolithic_count: int = 0,
) -> float:
    """Return the total forage required for the next fill."""
    bonus = 1 + 0.02 / (monolithic_count / 5 + 1)
    return (base + fills) * (bonus**fills)


def simulate_progressive(
    territory: Territory,
    team_a: Team,
    team_b: Team,
    label_a: str,
    label_b: str,
    max_hours: int,
    stop_at_breakeven: bool = True,
) -> Iterator[tuple[list[float], list[float], list[float], Optional[float]]]:
    """Simulate two teams collecting spices over time and yield progress step by step."""

    def init_state(team: Team) -> dict[str, float | int]:
        return {
            "spice": 0.0,
            "fills": 0,
            "progress": 0.0,
            "speed": team.speed,
            "alchemic": count_genetic(team, ALCHEMIC),
            "monolithic": count_genetic(team, MONOLITHIC),
        }

    def next_fill_time(state: dict[str, float | int]) -> float:
        if state["speed"] <= 0:
            return float("inf")
        req = calculate_forage_requirement(
            territory.forage,
            int(state["fills"]),
            int(state["monolithic"]),
        )
        return (req - float(state["progress"])) / float(state["speed"])

    a = init_state(team_a)
    b = init_state(team_b)

    timeline = [0.0]
    a_yield = [0.0]
    b_yield = [0.0]
    breakeven: float | None = None
    t = 0.0

    while t <= max_hours:
        dt = min(next_fill_time(a), next_fill_time(b))
        t += dt
        if t > max_hours:
            break

        for state in (a, b):
            state["progress"] += state["speed"] * dt
            req = calculate_forage_requirement(
                territory.forage,
                int(state["fills"]),
                int(state["monolithic"]),
            )

            if state["progress"] >= req:
                state["fills"] += 1
                state["spice"] += 1 + 0.5 * state["alchemic"]
                state["progress"] = 0.0

        timeline.append(t)
        a_yield.append(a["spice"])
        b_yield.append(b["spice"])

        if breakeven is None and b["spice"] > a["spice"]:
            breakeven = t
            if stop_at_breakeven:
                yield timeline, a_yield, b_yield, breakeven
                return

        yield timeline, a_yield, b_yield, breakeven
