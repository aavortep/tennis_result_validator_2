from django.db import transaction
from django.utils import timezone

from shared.clients.user_service_client import UserServiceClient
from shared.clients.tournaments_service_client import TournamentsServiceClient
from apps.scores.internal.score import Score
from apps.evidence.internal.evidence import Evidence
from shared.exceptions import (
    DisputeError,
    InvalidStateError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)

from .internal.dispute import Dispute


class DisputeService:
    @staticmethod
    def create_dispute(match_id, reason, user):
        match = TournamentsServiceClient.get_match(match_id)
        if match is None:
            raise NotFoundError("Match not found.")

        if not user.is_player or not match.is_player_in_match(user):
            raise PermissionDeniedError(
                "Only players in this match can raise disputes."
            )

        existing_dispute = Dispute.objects.filter(
            match=match, status__in=[Dispute.Status.OPEN, Dispute.Status.UNDER_REVIEW]
        ).exists()
        if existing_dispute:
            raise DisputeError("There is already an open dispute for this match.")

        dispute = Dispute.objects.create(match=match.id, raised_by=user.id, reason=reason)

        match.status = "DISPUTED"
        match.save()

        return dispute

    @staticmethod
    def add_evidence(dispute_id, file, description, user):
        try:
            dispute = Dispute.objects.get(id=dispute_id)
        except Dispute.DoesNotExist:
            raise NotFoundError("Dispute not found.")

        if dispute.status == Dispute.Status.RESOLVED:
            raise InvalidStateError("Cannot add evidence to resolved dispute.")

        match = TournamentsServiceClient.get_match(dispute.match)
        if user.is_player:
            if not match.is_player_in_match(user):
                raise PermissionDeniedError("You are not a player in this match.")
        elif not (user.is_referee or user.is_organizer):
            raise PermissionDeniedError("Only involved parties can submit evidence.")

        evidence = Evidence.objects.create(
            dispute=dispute, submitted_by=user.id, file=file, description=description
        )

        return evidence

    @staticmethod
    @transaction.atomic
    def resolve_dispute(dispute_id, resolution_notes, user, final_score_id=None, winner_id=None):
        try:
            dispute = Dispute.objects.get(id=dispute_id)
        except Dispute.DoesNotExist:
            raise NotFoundError("Dispute not found.")

        if not (user.is_referee or user.is_organizer):
            raise PermissionDeniedError(
                "Only referees and organizers can resolve disputes."
            )

        match = TournamentsServiceClient.get_match(dispute.match)

        if user.is_referee and match.referee != user.id:
            raise PermissionDeniedError("You are not the referee for this match.")

        if dispute.status == Dispute.Status.RESOLVED:
            raise InvalidStateError("Dispute is already resolved.")

        final_score = None
        if final_score_id:
            try:
                final_score = Score.objects.get(id=final_score_id, match=match)
            except Score.DoesNotExist:
                raise NotFoundError("Final score not found.")

        winner = None
        if winner_id:
            winner = UserServiceClient.get_user(winner_id)
            if winner is None:
                raise NotFoundError("Winner not found.")
            if not match.is_player_in_match(winner):
                raise ValidationError("Winner must be a player in the match.")
        elif final_score:
            winner = UserServiceClient.get_user(final_score.winner)

        dispute.status = Dispute.Status.RESOLVED
        dispute.resolved_by = user.id
        dispute.resolution_notes = resolution_notes
        dispute.resolved_at = timezone.now()
        dispute.final_score = final_score
        dispute.save()

        match.status = "COMPLETED"
        match.winner = winner.id
        match.save()

        return dispute

    @staticmethod
    def get_dispute_evidence(dispute_id):
        return Evidence.objects.filter(dispute_id=dispute_id)

    @staticmethod
    def get_open_disputes():
        return Dispute.objects.filter(
            status__in=[Dispute.Status.OPEN, Dispute.Status.UNDER_REVIEW]
        )

    @staticmethod
    def mark_under_review(dispute_id, user):
        try:
            dispute = Dispute.objects.get(id=dispute_id)
        except Dispute.DoesNotExist:
            raise NotFoundError("Dispute not found.")

        if not (user.is_referee or user.is_organizer):
            raise PermissionDeniedError(
                "Only referees and organizers can review disputes."
            )

        dispute.status = Dispute.Status.UNDER_REVIEW
        dispute.save()

        return dispute
