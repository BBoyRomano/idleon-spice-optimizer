"""Constants for the Idleon Spice Optimizer app."""

# JSON field keys
ID = "id"
NAME = "name"
FIGHT = "fight"
FORAGE = "forage"

# Simulation configuration
MAX_SIMULATION_HOURS = 48

# Team constraints
MAX_TEAM_SIZE = 4

# Default team labels
META_TEAM = "Meta Team"
ALCHEMIC_TEAM = "Alchemic Team"

# Default team compositions by label (resolved by genetic name)
DEFAULT_TEAMS = {
    META_TEAM: ["Borger", "Miasma", "Forager", "Converter"],
    ALCHEMIC_TEAM: ["Alchemic", "Alchemic", "Alchemic", "Converter"],
}

# Asset path constants
GENETIC_ASSETS_PATH = "assets/genetics"
SPICE_ASSETS_PATH = "assets/spices"
TERRITORY_ASSETS_PATH = "assets/territories"
