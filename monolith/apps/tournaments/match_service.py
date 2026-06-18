from django.db import models

from apps.users.internal.user import User
from apps.users.web.roles import Role
from shared.exceptions import (
    InvalidStateError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)
from .internal.tournament import Tournament
from .internal.match import Match
from .internal.helpers import to_match_dto


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
            player1=data.get("player1"),
            player2=data.get("player2"),
            referee=data.get("referee"),
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

        try:
            player1 = User.objects.get(id=player1_id, role=Role.PLAYER)
            player2 = User.objects.get(id=player2_id, role=Role.PLAYER)
        except User.DoesNotExist:
            raise NotFoundError("Player not found.")
        
        if (not match.tournament.players.filter(id__in=[player1_id, player2_id]).count() == 2):
            raise ValidationError("Both players must be registered in the tournament.")

        match.player1 = player1
        match.player2 = player2
        match.save()
        return match

    @staticmethod
    def assign_referee(match, referee_id, user):
        if not user.is_organizer:
            raise PermissionDeniedError("Only organizers can assign referees.")

        try:
            referee = User.objects.get(id=referee_id, role=Role.REFEREE)
        except User.DoesNotExist:
            raise NotFoundError("Referee not found.")

        match.referee = referee
        match.save()
        return match

    @staticmethod
    def start_match(match, user):
        if not (user.is_organizer or (user.is_referee and match.referee == user)):
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
            matches = Match.objects.filter(referee=user)
            return [to_match_dto(match) for match in matches]
        elif user.is_player:
            matches = Match.objects.filter(models.Q(player1=user) | models.Q(player2=user))
            return [to_match_dto(match) for match in matches]
        return Match.objects.none()

    @staticmethod
    def get_match_by_id(match_id):
        try:
            match = Match.objects.get(id=match_id)
            return to_match_dto(match)
        except Match.DoesNotExist:
            raise NotFoundError("Match not found.")
