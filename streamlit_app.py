"""Run the Streamlit app for the Idleon Spice Optimizer."""

import pandas as pd
import streamlit as st

from constants import ALCHEMIC_TEAM, DEFAULT_TEAMS, MAX_SIMULATION_HOURS, META_TEAM
from loader import (
    build_genetics_by_name,
    build_territories_by_name,
    load_genetics,
    load_territories,
)
from models import Pet, Team, Territory
from simulation import simulate_progressive
from utils import format_number, format_time, image_to_base64_uri, slugify


def display_team(team: Team, label: str) -> None:
    """Render a single team with icons and speed caption."""
    st.subheader(label, anchor=False)
    icon_cols = st.columns(len(team.pets))
    for pet, col in zip(team.pets, icon_cols, strict=True):
        with col:
            st.image(pet.genetic.icon_path, use_container_width=True)
    st.caption(f"Speed: {format_number(team.speed)}")


def display_teams(team_a: Team, label_a: str, team_b: Team, label_b: str) -> None:
    """Render two teams side by side."""
    col1, col2 = st.columns(2)
    with col1:
        display_team(team_a, label_a)
    with col2:
        display_team(team_b, label_b)


def append_chart_data(
    chart,
    timeline: list[float],
    team_a_yield: list[float],
    team_b_yield: list[float],
    label_a: str,
    label_b: str,
) -> None:
    """Append the latest simulation step to the chart."""
    if not timeline:
        return

    new_row: pd.DataFrame = pd.DataFrame({
        "Time (Hours)": [timeline[-1]],
        label_a: [team_a_yield[-1]],
        label_b: [team_b_yield[-1]],
    }).set_index("Time (Hours)")
    chart.add_rows(new_row)


def display_breakeven(
    breakeven: float | None,
    label_a: str,
    label_b: str,
    max_hours: int,
) -> None:
    """Display the breakeven result message."""
    if breakeven is not None:
        st.success(
            f"**{label_b}** surpasses **{label_a}** after **{format_time(breakeven)}**.",
            icon="✅",
        )
    else:
        st.warning(
            f"No breakeven found within **{format_time(max_hours)}**.",
            icon="⚠️",
        )


def display_breakeven_instructions(label_a: str, label_b: str) -> None:
    """Display usage guidance for breakeven interpretation."""
    st.info(
        f"""
        **How to use the Breakeven Time:**
        - Claim **more often** than breakeven? Stick with **{label_a}**
        - Claim **less often**? Use **{label_b}** for long-term stacking

        **Tip:** The **Converter** gives 50% chance to avoid consuming your stack — free spices!
        """,
        icon="🧠"
    )


def render_territory_comparison(
    territory: Territory,
    team_a: Team,
    team_b: Team,
    label_a: str,
    label_b: str,
    max_hours: int,
    show_extras: bool = True,
) -> None:
    """Render one simulation card with teams, chart, and breakeven message."""
    bg_uri = image_to_base64_uri(territory.background_path)
    slug = slugify(territory.name)

    st.markdown(
        f"""
        <style>
        .st-key-comparison-{slug} {{
            background-image: url("{bg_uri}");
            background-size: cover;
            background-position: center;
            padding: 2rem;
            border-radius: 1rem;
            position: relative;
            overflow: hidden;
        }}
        .st-key-comparison::before {{
            content: "";
            position: absolute;
            inset: 0;
            background: rgba(0, 0, 0, 0.5);  /* semi-dark overlay */
            border-radius: 1rem;
            z-index: 0;
        }}
        .st-key-comparison > * {{
            position: relative;
            z-index: 1;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.container(key=f"comparison-{slug}"):
        st.header(territory.name)

        breakeven = None
        chart = None

        if show_extras:
            display_teams(team_a, label_a, team_b, label_b)
            chart = st.line_chart(pd.DataFrame(columns=[label_a, label_b]))

        for timeline, a_yield, b_yield, breakeven in simulate_progressive(
            territory=territory,
            team_a=team_a,
            team_b=team_b,
            label_a=label_a,
            label_b=label_b,
            max_hours=max_hours,
        ):
            if chart:
                append_chart_data(chart, timeline, a_yield,
                                  b_yield, label_a, label_b)

        display_breakeven(breakeven, label_a, label_b, max_hours)

        if show_extras:
            display_breakeven_instructions(label_a, label_b)


def render_all_territory_comparisons(
    territories: list[Territory],
    team_a: Team,
    team_b: Team,
    label_a: str,
    label_b: str,
    max_hours: int,
) -> None:
    """Render simulation cards for all territories without charts."""
    for territory in territories:
        render_territory_comparison(
            territory,
            team_a,
            team_b,
            label_a,
            label_b,
            max_hours,
            show_extras=False
        )


def main() -> None:
    """Run the Idleon Spice Optimizer app in Streamlit."""
    st.set_page_config(page_title="Idleon Spice Optimizer", page_icon="🌶️")
    st.title("🌶️ Idleon Spice Optimizer")
    st.caption("Optimize your foraging. Maximize your spices.")
    st.markdown(
        """
        **Ready to boost your spice game?**
        Whether you claim hourly or AFK for days, this app helps you maximize your spice gains — **fast and easy**.
        """
    )

    with st.sidebar:
        st.header("⚙️ Configuration")
        st.text("")

        st.subheader("⚔️ Normal vs Alchemic Team")

        territories = load_territories()
        territory_lookup = build_territories_by_name(territories)
        territory_selected = st.selectbox(
            "Select Territory", list(territory_lookup))

        non_alchemic_speed = st.number_input(
            "Non-Alchemic Foraging Speed",
            min_value=0,
            help="Average foraging speed without Alchemics.",
        )
        alchemic_speed = st.number_input(
            "Alchemic Foraging Speed",
            min_value=0,
            help="Average foraging speed with 3 Alchemics and 1 Converter.",
        )

        col1, col2 = st.columns(2)
        with col1:
            compare_clicked = st.button(
                "Compare", type="primary", use_container_width=True)
        with col2:
            compare_all_clicked = st.button(
                "Compare All", use_container_width=True)

        st.divider()
        st.subheader("📥 Import Data (Coming Soon)")
        raw_data = st.text_area(
            "Paste Idleon Data",
            disabled=True,
            help="Paste your Idleon data from Idleon Efficiency or Idleon Toolbox.",
        )
        import_clicked = st.button(
            "Import",
            type="primary",
            disabled=not raw_data.strip(),
            use_container_width=True,
        )

        st.divider()
        st.subheader("☕ Support Development")
        st.markdown(
            "[![Support Me](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/bboyromano)",
            unsafe_allow_html=True,
        )

    if compare_clicked or compare_all_clicked:
        genetics = load_genetics()
        genetics_by_name = build_genetics_by_name(genetics)

        meta_team = Team(
            name=META_TEAM,
            manual_speed=non_alchemic_speed,
            pets=[
                Pet(genetic=genetics_by_name[gene])
                for gene in DEFAULT_TEAMS[META_TEAM]
            ],
        )

        alchemic_team = Team(
            name=ALCHEMIC_TEAM,
            manual_speed=alchemic_speed,
            pets=[
                Pet(genetic=genetics_by_name[gene])
                for gene in DEFAULT_TEAMS[ALCHEMIC_TEAM]
            ],
        )

        if compare_clicked:
            render_territory_comparison(
                territory=territory_lookup[territory_selected],
                team_a=meta_team,
                team_b=alchemic_team,
                label_a="Non-Alchemic",
                label_b="Alchemic",
                max_hours=MAX_SIMULATION_HOURS,
            )

        elif compare_all_clicked:
            render_all_territory_comparisons(
                territories=territories,
                team_a=meta_team,
                team_b=alchemic_team,
                label_a="Non-Alchemic",
                label_b="Alchemic",
                max_hours=MAX_SIMULATION_HOURS,
            )

    elif import_clicked:
        pass

    else:
        st.info(
            "Use the Sidebar to start optimizing your spice gains!",
            icon="ℹ️",
        )


if __name__ == "__main__":
    main()
