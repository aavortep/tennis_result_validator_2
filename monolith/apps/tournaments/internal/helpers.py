from apps.tournaments.dto.match_dto import MatchDTO
from apps.tournaments.dto.tournament_dto import TournamentDTO
from apps.users.internal.helpers import to_user_dto

def to_match_dto(match):
    return MatchDTO(
        match.id,
        match.scheduled_time,
        match.court,
        match.round,
        match.status,
        to_user_dto(match.player1),
        to_user_dto(match.player2),
        to_user_dto(match.referee),
        to_tournament_dto(match.tournament),
        to_user_dto(match.winner)
    )

def to_tournament_dto(tournament):
    return TournamentDTO(
        tournament.id,
        tournament.name,
        tournament.description,
        tournament.start_date,
        tournament.end_date,
        tournament.location,
        tournament.status,
        [to_user_dto(player) for player in tournament.players],
        [to_user_dto(referee) for referee in tournament.referees]
    )
