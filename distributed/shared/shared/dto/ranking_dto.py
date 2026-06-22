from dataclasses import dataclass


@dataclass
class RankingDTO:
    id: int
    points: int
    wins: int
    losses: int
    sets_won: int
    sets_lost: int
    games_won: int
    games_lost: int
    position: int
    player: int
    tournament: int
