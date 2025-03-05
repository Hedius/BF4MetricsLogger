from dataclasses import dataclass


@dataclass
class StatsEntry:
    mode: str = 'unknown'
    map: str = 'unknown'
    players: int = 0
    queue: int = 0
    favorites: int = 0
