from django.utils import timezone

from shared.clients.tournaments_service_client import TournamentsServiceClient
from shared.exceptions import (
    InvalidStateError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)
from shared.utils import determine_match_winner, validate_set_scores
from shared.dto.helpers import to_score_dto

from .internal.score import Score


class ScoreService:
    @staticmethod
    def submit_score(match_id, set_scores, user):
        match = TournamentsServiceClient.get_match(match_id)
        if match is None:
            raise NotFoundError("Match not found.")

        if user.is_player:
            if not match.is_player_in_match(user):
                raise PermissionDeniedError("You are not a player in this match.")
        elif user.is_referee:
            if match.referee != user.id:
                raise PermissionDeniedError("You are not the referee for this match.")
        else:
            raise PermissionDeniedError("Only players and referees can submit scores.")

        if match.status not in ("IN_PROGRESS", "COMPLETED"):
            raise InvalidStateError(
                "Match must be in progress or completed to submit score."
            )

        is_valid, error = validate_set_scores(set_scores)
        if not is_valid:
            raise ValidationError(error)

        existing_score = Score.objects.filter(match=match.id, submitted_by=user.id).first()
        if existing_score:
            raise ValidationError("You have already submitted a score for this match.")

        winner_key = determine_match_winner(set_scores)
        winner = None
        if winner_key:
            winner = match.player1 if winner_key == "player1" else match.player2

        score = Score.objects.create(
            match=match.id,
            submitted_by=user.id,
            set_scores=set_scores,
            winner=winner,
            is_confirmed=user.is_referee,
        )

        if user.is_referee:
            ScoreService._finalize_match(match, score)

        return score

    @staticmethod
    def update_score(score_id, set_scores, user):
        try:
            score = Score.objects.get(id=score_id)
        except Score.DoesNotExist:
            raise NotFoundError("Score not found.")

        if score.submitted_by != user.id:
            raise PermissionDeniedError(
                "You can only update your own score submission."
            )

        if score.is_confirmed:
            raise InvalidStateError("Cannot update confirmed score.")

        is_valid, error = validate_set_scores(set_scores)
        if not is_valid:
            raise ValidationError(error)

        winner_key = determine_match_winner(set_scores)
        winner = None
        if winner_key:
            match = TournamentsServiceClient.get_match(score.match)
            winner = match.player1 if winner_key == "player1" else match.player2

        score.set_scores = set_scores
        score.winner = winner
        score.save()

        return score

    @staticmethod
    def delete_score(score_id, user):
        try:
            score = Score.objects.get(id=score_id)
        except Score.DoesNotExist:
            raise NotFoundError("Score not found.")

        if score.submitted_by != user.id and not user.is_organizer:
            raise PermissionDeniedError(
                "You can only delete your own score submission."
            )

        if score.is_confirmed and not user.is_organizer:
            raise InvalidStateError("Cannot delete confirmed score.")

        score.delete()

    @staticmethod
    def confirm_score(score_id, user):
        try:
            score = Score.objects.get(id=score_id)
        except Score.DoesNotExist:
            raise NotFoundError("Score not found.")

        match = TournamentsServiceClient.get_match(score.match)

        if user.is_player:
            if not match.is_player_in_match(user):
                raise PermissionDeniedError("You are not a player in this match.")
            if score.submitted_by == user.id:
                raise ValidationError("You cannot confirm your own score.")

        elif user.is_referee:
            if match.referee != user.id:
                raise PermissionDeniedError("You are not the referee for this match.")
        else:
            raise PermissionDeniedError("Only players and referees can confirm scores.")

        if score.is_confirmed:
            raise ValidationError("Score is already confirmed.")

        score.is_confirmed = True
        score.confirmed_by = user.id
        score.confirmed_at = timezone.now()
        score.save()

        ScoreService._finalize_match(match, score)

        return score

    @staticmethod
    def _finalize_match(match, score):
        match.status = "COMPLETED"
        match.winner = score.winner
        match.save()

    @staticmethod
    def get_match_scores(match_id):
        score = Score.objects.filter(match_id=match_id)
        return to_score_dto(score)
