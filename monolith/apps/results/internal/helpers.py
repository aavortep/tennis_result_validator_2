from apps.results.score_dto import ScoreDTO
from apps.users.internal.helpers import to_user_dto
from apps.tournaments.internal.helpers import to_match_dto

def to_score_dto(score):
    return ScoreDTO(
        score.id,
        score.is_confirmed,
        to_user_dto(score.confirmed_by),
        to_match_dto(score.match),
        to_user_dto(score.submitted_by),
        to_user_dto(score.winner),
    )
