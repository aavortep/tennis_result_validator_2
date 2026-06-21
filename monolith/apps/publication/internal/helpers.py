from apps.publication.dto.ranking_dto import RankingDTO
from apps.publication.dto.global_ranking_dto import GlobalRankingDTO
from apps.users.internal.helpers import to_user_dto
from apps.tournaments.internal.helpers import to_tournament_dto

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
        to_user_dto(ranking.player),
        to_tournament_dto(ranking.tournament),
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
        to_user_dto(ranking.player),
    )
