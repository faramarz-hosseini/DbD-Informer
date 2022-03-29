class MsgField:
    K_RANK = ":knife: Killer Rank"
    S_RANK = ":woman_running: Survivor Rank"
    TOTAL_BP = ":drop_of_blood: Total Bloodpoints"
    PIP_SCORE = ":medal: Pip Score"
    PLAY_TIME = ":hourglass: Time Played"
    ESCAPES = ":door: Total Escapes"
    GENS_DONE = ":wrench: Generators Repaired"
    SAC_SURVS = ":dagger: Survivors Sacrificed"
    BASEMENT_HOOKED = ":house_abandoned: Survivors Hooked in Basement"


DBD_RANK_PIPS = {
    0: "Ash IV",
    3: "Ash III",
    6: "Ash II",
    10: "Ash I",
    14: "Bronze IV",
    18: "Bronze III",
    22: "Bronze II",
    26: "Bronze I",
    30: "Silver IV",
    35: "Silver III",
    40: "Silver II",
    45: "Silver I",
    50: "Gold IV",
    55: "Gold III",
    60: "Gold II",
    65: "Gold I",
    70: "Iridescent IV",
    75: "Iridescent III",
    80: "Iridescent II",
    85: "Iridescent I",
}

STEAM_STATS = (
    MsgField.PLAY_TIME,
)

DBD_STATS_MAP = {
    "DBD_KillerSkulls": MsgField.K_RANK,
    "DBD_CamperSkulls": MsgField.S_RANK,
    "DBD_Escape": MsgField.ESCAPES,
    "DBD_GeneratorPct_float": MsgField.GENS_DONE,
    "DBD_SacrificedCampers": MsgField.SAC_SURVS,
    "DBD_DLC6_Slasher_Stat2": MsgField.BASEMENT_HOOKED,
    "DBD_BloodwebPoints": MsgField.TOTAL_BP,
    "DBD_UnlockRanking": MsgField.PIP_SCORE,
}

SPACE_NEEDED_FIELDS = (
    MsgField.S_RANK,
    MsgField.PLAY_TIME,
    MsgField.GENS_DONE,
    MsgField.BASEMENT_HOOKED,
)

SHRINE_MSG = "**Available perks in Shrine right now:**\n\n" \
              " 1) {}\n 2) {}\n 3) {}\n 4) {}\n\n" \
              "**Shrine of Secrets resets in: {} day(s) and {} hour(s)**"
RANK_RESET_MSG = "Rank reset happens in: {} day(s) and {} hour(s)"
