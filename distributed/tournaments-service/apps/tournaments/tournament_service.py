from shared.clients.user_service_client import UserServiceClient
from shared.roles import Role
from shared.exceptions import (
    InvalidStateError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)

from .internal.tournament import Tournament, TournamentPlayer, TournamentReferee
from shared.dto.helpers import to_tournament_dto, to_match_dto


class TournamentService:
    @staticmethod
    def create_tournament(data, created_by):
        if not created_by.is_organizer:
            raise PermissionDeniedError("Only organizers can create tournaments.")

        tournament = Tournament.objects.create(
            name=data["name"],
            description=data.get("description", ""),
            start_date=data["start_date"],
            end_date=data["end_date"],
            location=data["location"],
            max_players=data.get("max_players", 32),
            created_by=created_by,
        )
        return tournament

    @staticmethod
    def update_tournament(tournament, data, user):
        if not user.is_organizer:
            raise PermissionDeniedError("Only organizers can update tournaments.")

        if tournament.status in (
            Tournament.Status.COMPLETED,
            Tournament.Status.CANCELLED,
        ):
            raise InvalidStateError("Cannot update completed or cancelled tournament.")

        for field, value in data.items():
            if hasattr(tournament, field):
                setattr(tournament, field, value)
        tournament.save()
        return tournament

    @staticmethod
    def delete_tournament(tournament, user):
        if not user.is_organizer:
            raise PermissionDeniedError("Only organizers can delete tournaments.")

        if tournament.status == Tournament.Status.IN_PROGRESS:
            raise InvalidStateError("Cannot delete tournament in progress.")

        tournament.delete()

    @staticmethod
    def add_player(tournament, player_id, user):
        if not user.is_organizer:
            raise PermissionDeniedError("Only organizers can add players.")

        if tournament.status not in (
            Tournament.Status.DRAFT,
            Tournament.Status.REGISTRATION,
        ):
            raise InvalidStateError("Cannot add players after registration closes.")

        player = UserServiceClient.get_user(player_id)
        if player is None:
            raise NotFoundError("Player not found.")

        tournament_players = tournament.get_player_ids()
        if len(tournament_players) >= tournament.max_players:
            raise ValidationError("Tournament is full.")

        if player_id in tournament_players:
            raise ValidationError("Player already in tournament.")

        TournamentPlayer.objects.create(
            tournament=tournament,
            player_id=player_id
        )
        return tournament

    @staticmethod
    def remove_player(tournament, player_id, user):
        if not user.is_organizer:
            raise PermissionDeniedError("Only organizers can remove players.")

        if tournament.status == Tournament.Status.IN_PROGRESS:
            raise InvalidStateError(
                "Cannot remove players from tournament in progress."
            )

        TournamentPlayer.objects.filter(
            tournament=tournament,
            player_id=player_id
        ).delete()

    @staticmethod
    def add_referee(tournament, referee_id, user):
        if not user.is_organizer:
            raise PermissionDeniedError("Only organizers can add referees.")

        referee = UserServiceClient.get_user(referee_id)
        if referee is None:
            raise NotFoundError("Referee not found.")

        tournament_referees = tournament.get_referee_ids()
        if referee_id in tournament_referees:
            raise ValidationError("Referee already in tournament.")

        TournamentReferee.objects.create(
            tournament=tournament,
            referee_id=referee_id
        )
        return tournament

    @staticmethod
    def open_registration(tournament, user):
        if not user.is_organizer:
            raise PermissionDeniedError("Only organizers can open registration.")

        if tournament.status != Tournament.Status.DRAFT:
            raise InvalidStateError("Can only open registration for draft tournaments.")

        tournament.status = Tournament.Status.REGISTRATION
        tournament.save()
        return tournament

    @staticmethod
    def start_tournament(tournament, user):
        if not user.is_organizer:
            raise PermissionDeniedError("Only organizers can start tournaments.")

        if tournament.status != Tournament.Status.REGISTRATION:
            raise InvalidStateError("Tournament must be in registration to start.")

        tournament_players = tournament.get_player_ids()
        if len(tournament_players) < 2:
            raise ValidationError("Tournament needs at least 2 players to start.")

        tournament.status = Tournament.Status.IN_PROGRESS
        tournament.save()
        return tournament

    @staticmethod
    def complete_tournament(tournament, user):
        if not user.is_organizer:
            raise PermissionDeniedError("Only organizers can complete tournaments.")

        tournament.status = Tournament.Status.COMPLETED
        tournament.save()
        return tournament

    @staticmethod
    def get_tournament_matches(tournament):
        matches = tournament.matches.all()
        return [to_match_dto(match) for match in matches]

    @staticmethod
    def get_user_tournaments(user):
        tournaments = Tournament.objects.filter(
            status__in=[Tournament.Status.REGISTRATION, Tournament.Status.IN_PROGRESS]
        )
        if user.is_organizer:
            tournaments = Tournament.objects.filter(created_by=user)
        elif user.is_player:
            tournaments = user.tournaments.all()
        elif user.is_referee:
            tournaments = user.referee_tournaments.all()
        return [to_tournament_dto(tournament) for tournament in tournaments]
