import requests
from ..dto.score_dto import ScoreDTO
from ..dto.dispute_dto import DisputeDTO


class ResultsServiceClient:

    BASE_URL = "http://results-service:8002"

    def json_to_score_dto(score):
        return ScoreDTO(
            id=score["id"],
            is_confirmed=score["is_confirmed"],
            confirmed_by=score["confirmed_by"],
            match=score["match"],
            submitted_by=score["submitted_by"],
            winner=score["winner"]
        )

    @classmethod
    def get_scores_by_match(cls, match_id: int):
        response = requests.get(
            f"{cls.BASE_URL}/api/scores/match/{match_id}"
        )

        response.raise_for_status()
        data = response.json()

        return [cls.json_to_score_dto(score) for score in data]
    
    @classmethod
    def get_disputes_by_match(cls, match_id: int):
        response = requests.get(
            f"{cls.BASE_URL}/api/validation/match/{match_id}"
        )

        response.raise_for_status()
        data = response.json()

        return [DisputeDTO(
            id=dispute["id"],
            reason=dispute["reason"],
            status=dispute["status"],
            resolution_notes=dispute["resolution_notes"],
            final_score=cls.json_to_score_dto(dispute["final_score"]),
            match=dispute["match"],
            raised_by=dispute["raised_by"],
            resolved_by=dispute["resolved_by"]
        ) for dispute in data]
