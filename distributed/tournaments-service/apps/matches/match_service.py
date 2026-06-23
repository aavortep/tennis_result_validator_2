from django.db import models

from shared.exceptions import (
    InvalidStateError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)
from shared.dto.helpers import to_match_dto
from shared.clients.user_service_client import UserServiceClient
from apps.tournaments.internal.tournament import Tournament
from .internal.match import Match


class MatchService:
    @staticmethod
    def create_match(data, user):
        if not user.is_organizer:
            raise PermissionDeniedError("Only organizers can create matches.")

        tournament = data["tournament"]
        if tournament.status not in (
            Tournament.Status.REGISTRATION,
            Tournament.Status.IN_PROGRESS,
        ):
            raise InvalidStateError("Cannot create matches for this tournament.")

        match = Match.objects.create(
            tournament=tournament,
            player1_id=data.get("player1"),
            player2_id=data.get("player2"),
            referee_id=data.get("referee"),
            scheduled_time=data.get("scheduled_time"),
            court=data.get("court", ""),
            round=data.get("round", Match.Round.ROUND_32),
        )
        return match

    @staticmethod
    def assign_players(match, player1_id, player2_id, user):
        if not user.is_organizer:
            raise PermissionDeniedError("Only organizers can assign players.")

        if match.status != Match.Status.SCHEDULED:
            raise InvalidStateError("Can only assign players to scheduled matches.")

        player1 = UserServiceClient.get_user(player1_id)
        player2 = UserServiceClient.get_user(player2_id)
        if player1 is None or player2 is None:
            raise NotFoundError("Player not found.")
        
        tournament_players = match.tournament.get_player_ids()
        if (not player1_id in tournament_players) or (not player2_id in tournament_players):
            raise ValidationError("Both players must be registered in the tournament.")

        match.player1_id = player1.id
        match.player2_id = player2.id
        match.save()
        return match

    @staticmethod
    def assign_referee(match, referee_id, user):
        if not user.is_organizer:
            raise PermissionDeniedError("Only organizers can assign referees.")

        referee = UserServiceClient.get_user(referee_id)
        if referee is None:
            raise NotFoundError("Referee not found.")

        match.referee_id = referee.id
        match.save()
        return match

    @staticmethod
    def start_match(match, user):
        if not (user.is_organizer or (user.is_referee and match.referee_id == user.id)):
            raise PermissionDeniedError(
                "Only organizers or assigned referee can start match."
            )

        if match.status != Match.Status.SCHEDULED:
            raise InvalidStateError("Match must be scheduled to start.")

        if not match.is_player_assigned:
            raise ValidationError("Both players must be assigned to start match.")

        match.status = Match.Status.IN_PROGRESS
        match.save()
        return match

    @staticmethod
    def get_user_matches(user):
        if user.is_referee:
            matches = Match.objects.filter(referee_id=user.id)
            return [to_match_dto(match) for match in matches]
        elif user.is_player:
            matches = Match.objects.filter(models.Q(player1_id=user.id) | models.Q(player2_id=user.id))
            return [to_match_dto(match) for match in matches]
        return Match.objects.none()

    @staticmethod
    def get_match_by_id(match_id):
        try:
            match = Match.objects.get(id=match_id)
            return to_match_dto(match)
        except Match.DoesNotExist:
            raise NotFoundError("Match not found.")
