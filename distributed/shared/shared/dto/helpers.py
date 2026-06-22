from .user_dto import UserDTO
from .match_dto import MatchDTO
from .tournament_dto import TournamentDTO
from .score_dto import ScoreDTO
from .dispute_dto import DisputeDTO
from .ranking_dto import RankingDTO
from .global_ranking_dto import GlobalRankingDTO

def to_user_dto(user):
    return UserDTO(
        user.id,
        user.username,
        user.first_name,
        user.last_name,
        user.email,
        user.role,
        user.phone,
        user.bio
    )

def to_match_dto(match):
    return MatchDTO(
        match.id,
        match.scheduled_time,
        match.court,
        match.round,
        match.status,
        match.player1_id,
        match.player2_id,
        match.referee_id,
        to_tournament_dto(match.tournament),
        match.winner_id
    )

def to_tournament_dto(tournament):
    return TournamentDTO(
        tournament.id,
        tournament.name,
        tournament.description,
        tournament.start_date,
        tournament.end_date,
        tournament.location,
        tournament.status
    )

def to_score_dto(score):
    return ScoreDTO(
        score.id,
        score.is_confirmed,
        score.confirmed_by,
        score.match,
        score.submitted_by,
        score.winner,
    )

def to_dispute_dto(dispute):
    return DisputeDTO(
        dispute.id,
        dispute.reason,
        dispute.status,
        dispute.resolution_notes,
        to_score_dto(dispute.final_score),
        dispute.match,
        dispute.raised_by,
        dispute.resolved_by,
    )

def to_ranking_dto(ranking):
    return RankingDTO(
        ranking.id,
        ranking.points,
        ranking.wins,
        ranking.losses,
        ranking.sets_won,
        ranking.sets_lost,
        ranking.games_won,
        ranking.games_lost,
        ranking.position,
        ranking.player,
        ranking.tournament,
    )

def to_global_ranking_dto(ranking):
    return GlobalRankingDTO(
        ranking.id,
        ranking.total_points,
        ranking.total_wins,
        ranking.total_losses,
        ranking.tournaments_played,
        ranking.tournaments_won,
        ranking.position,
        ranking.player,
    )
