import requests
from ..dto.match_dto import MatchDTO
from ..dto.tournament_dto import TournamentDTO


class TournamentsServiceClient:

    BASE_URL = "http://tournaments-service:8001"

    def json_to_tournament_dto(tour):
        return TournamentDTO(
            id=tour["id"],
            name=tour["name"],
            description=tour["description"],
            start_date=tour["start_date"],
            end_date=tour["end_date"],
            location=tour["location"],
            status=tour["status"],
        )

    def json_to_match_dto(cls, match):
        return MatchDTO(
            id=match["id"],
            scheduled_time=match["scheduled_time"],
            court=match["court"],
            round=match["round"],
            status=match["status"],
            player1=match["player1"],
            player2=match["player2"],
            referee=match["referee"],
            tournament=cls.json_to_tournament_dto(match["tournament"]),
            winner=match["winner"]
        )

    @classmethod
    def get_match(cls, match_id: int):
        response = requests.get(
            f"{cls.BASE_URL}/api/matches/matches/{match_id}"
        )

        response.raise_for_status()
        data = response.json()

        return cls.json_to_match_dto(data)
    
    @classmethod
    def get_tournament(cls, tournament_id: int):
        response = requests.get(
            f"{cls.BASE_URL}/api/tournaments/{tournament_id}"
        )

        response.raise_for_status()
        data = response.json()

        return cls.json_to_tournament_dto(data)
    
    @classmethod
    def get_tournament_matches(cls, tournament_id: int):
        response = requests.get(
            f"{cls.BASE_URL}/api/tournaments/{tournament_id}/matches"
        )

        response.raise_for_status()
        data = response.json()

        return [cls.json_to_match_dto(match) for match in data]
