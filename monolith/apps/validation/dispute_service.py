from django.db import transaction
from django.utils import timezone

from apps.users.internal.user import User
from apps.tournaments.internal.match import Match
from apps.results.internal.score import Score
from shared.exceptions import (
    DisputeError,
    InvalidStateError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)

from .internal.dispute import Dispute
from .internal.evidence import Evidence


class DisputeService:
    @staticmethod
    def create_dispute(match_id, reason, user):
        try:
            match = Match.objects.get(id=match_id)
        except Match.DoesNotExist:
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

        dispute = Dispute.objects.create(match=match, raised_by=user, reason=reason)

        match.status = Match.Status.DISPUTED
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

        match = dispute.match
        if user.is_player:
            if not match.is_player_in_match(user):
                raise PermissionDeniedError("You are not a player in this match.")
        elif not (user.is_referee or user.is_organizer):
            raise PermissionDeniedError("Only involved parties can submit evidence.")

        evidence = Evidence.objects.create(
            dispute=dispute, submitted_by=user, file=file, description=description
        )

        return evidence

    @staticmethod
    @transaction.atomic
    def resolve_dispute(
        dispute_id, resolution_notes, user, final_score_id=None, winner_id=None
    ):
        try:
            dispute = Dispute.objects.get(id=dispute_id)
        except Dispute.DoesNotExist:
            raise NotFoundError("Dispute not found.")

        if not (user.is_referee or user.is_organizer):
            raise PermissionDeniedError(
                "Only referees and organizers can resolve disputes."
            )

        if user.is_referee and dispute.match.referee != user:
            raise PermissionDeniedError("You are not the referee for this match.")

        if dispute.status == Dispute.Status.RESOLVED:
            raise InvalidStateError("Dispute is already resolved.")

        match = dispute.match

        final_score = None
        if final_score_id:
            try:
                final_score = Score.objects.get(id=final_score_id, match=match)
            except Score.DoesNotExist:
                raise NotFoundError("Final score not found.")

        winner = None
        if winner_id:
            try:
                winner = User.objects.get(id=winner_id)
                if not match.is_player_in_match(winner):
                    raise ValidationError("Winner must be a player in the match.")
            except User.DoesNotExist:
                raise NotFoundError("Winner not found.")
        elif final_score:
            winner = final_score.winner

        dispute.status = Dispute.Status.RESOLVED
        dispute.resolved_by = user
        dispute.resolution_notes = resolution_notes
        dispute.resolved_at = timezone.now()
        dispute.final_score = final_score
        dispute.save()

        match.status = Match.Status.COMPLETED
        match.winner = winner
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
