from dataclasses import dataclass


@dataclass
class ScoreDTO:
    id: int
    is_confirmed: bool
    confirmed_by: int
    match: int
    submitted_by: int
    winner: int
