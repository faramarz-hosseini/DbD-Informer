from const import DBD_RANK_PIPS


def convert_pips_to_rank(pips: int) -> str:
    rank_pip_count = max([pip_count for pip_count in DBD_RANK_PIPS if pip_count <= pips])
    return DBD_RANK_PIPS[rank_pip_count]
