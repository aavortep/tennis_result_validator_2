from dataclasses import dataclass


@dataclass
class TournamentDTO:
    id: int
    name: str
    description: str
    start_date: str
    end_date: str
    location: str
    status: str
