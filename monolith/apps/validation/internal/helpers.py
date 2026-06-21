from apps.validation.dispute_dto import DisputeDTO
from apps.users.internal.helpers import to_user_dto
from apps.tournaments.internal.helpers import to_match_dto
from apps.results.internal.helpers import to_score_dto

def to_dispute_dto(dispute):
    return DisputeDTO(
        dispute.id,
        dispute.reason,
        dispute.status,
        dispute.resolution_notes,
        to_score_dto(dispute.final_score),
        to_match_dto(dispute.match),
        to_user_dto(dispute.raised_by),
        to_user_dto(dispute.resolved_by),
    )
