from django.db import transaction

from apps.results.internal.score import Score
from apps.tournaments.internal.match import Match

from .internal.ranking import Ranking
from .internal.global_ranking import GlobalRanking


class RankingService:
    ROUND_POINTS = {
        "R128": 10,
        "R64": 25,
        "R32": 50,
        "R16": 100,
        "QF": 200,
        "SF": 400,
        "F": 800,
    }

    WINNER_BONUS = 500

    @staticmethod
    @transaction.atomic
    def update_ranking_after_match(match):
        if match.status != Match.Status.COMPLETED or not match.winner:
            return

        tournament = match.tournament
        winner = match.winner
        loser = match.player1 if match.player2 == winner else match.player2

        winner_ranking, _ = Ranking.objects.get_or_create(
            player=winner, tournament=tournament
        )
        loser_ranking, _ = Ranking.objects.get_or_create(
            player=loser, tournament=tournament
        )

        round_points = RankingService.ROUND_POINTS.get(match.round, 50)

        winner_ranking.wins += 1
        winner_ranking.points += round_points

        loser_ranking.losses += 1
        loser_ranking.points += round_points // 4

        score = Score.objects.filter(match=match, is_confirmed=True).first()
        if score and score.set_scores:
            for set_score in score.set_scores:
                winner_games = (
                    set_score.get("player1", 0)
                    if winner == match.player1
                    else set_score.get("player2", 0)
                )
                loser_games = (
                    set_score.get("player1", 0)
                    if loser == match.player1
                    else set_score.get("player2", 0)
                )

                if winner_games > loser_games:
                    winner_ranking.sets_won += 1
                    loser_ranking.sets_lost += 1
                else:
                    winner_ranking.sets_lost += 1
                    loser_ranking.sets_won += 1

                winner_ranking.games_won += winner_games
                winner_ranking.games_lost += loser_games
                loser_ranking.games_won += loser_games
                loser_ranking.games_lost += winner_games

        winner_ranking.save()
        loser_ranking.save()

        RankingService.recalculate_positions(tournament)

    @staticmethod
    def recalculate_positions(tournament):
        rankings = Ranking.objects.filter(tournament=tournament).order_by(
            "-points", "-wins", "losses", "-sets_won"
        )

        for i, ranking in enumerate(rankings, 1):
            ranking.position = i
            ranking.save(update_fields=["position"])

    @staticmethod
    @transaction.atomic
    def finalize_tournament_rankings(tournament):
        final_match = Match.objects.filter(
            tournament=tournament,
            round=Match.Round.FINAL,
            status=Match.Status.COMPLETED,
        ).first()

        if final_match and final_match.winner:
            winner_ranking = Ranking.objects.filter(
                tournament=tournament, player=final_match.winner
            ).first()

            if winner_ranking:
                winner_ranking.points += RankingService.WINNER_BONUS
                winner_ranking.save()

        RankingService.recalculate_positions(tournament)

        for ranking in Ranking.objects.filter(tournament=tournament):
            RankingService.update_global_ranking(ranking.player)

    @staticmethod
    @transaction.atomic
    def update_global_ranking(player):
        global_ranking, created = GlobalRanking.objects.get_or_create(player=player)

        player_rankings = Ranking.objects.filter(player=player)

        global_ranking.total_points = sum(r.points for r in player_rankings)
        global_ranking.total_wins = sum(r.wins for r in player_rankings)
        global_ranking.total_losses = sum(r.losses for r in player_rankings)
        global_ranking.tournaments_played = player_rankings.count()
        global_ranking.tournaments_won = player_rankings.filter(position=1).count()
        global_ranking.save()

        RankingService.recalculate_global_positions()

    @staticmethod
    def recalculate_global_positions():
        rankings = GlobalRanking.objects.all().order_by(
            "-total_points", "-total_wins", "total_losses"
        )

        for i, ranking in enumerate(rankings, 1):
            ranking.position = i
            ranking.save(update_fields=["position"])

    @staticmethod
    def get_tournament_leaderboard(tournament_id):
        return (
            Ranking.objects.filter(tournament_id=tournament_id)
            .select_related("player")
            .order_by("position")
        )

    @staticmethod
    def get_global_leaderboard():
        return GlobalRanking.objects.select_related("player").order_by("position")

    @staticmethod
    def get_player_rankings(player_id):
        return (
            Ranking.objects.filter(player_id=player_id)
            .select_related("tournament")
            .order_by("-tournament__end_date")
        )

    @staticmethod
    def initialize_tournament_rankings(tournament):
        for player in tournament.players.all():
            Ranking.objects.get_or_create(player=player, tournament=tournament)

    @staticmethod
    def get_head_to_head(player1_id, player2_id):
        matches = (
            Match.objects.filter(
                status=Match.Status.COMPLETED,
                player1_id__in=[player1_id, player2_id],
                player2_id__in=[player1_id, player2_id],
            )
            .exclude(winner__isnull=True)
            .select_related("player1", "player2", "winner", "tournament")
            .order_by("-scheduled_time", "-created_at")
        )

        player1_wins = matches.filter(winner_id=player1_id).count()
        player2_wins = matches.filter(winner_id=player2_id).count()

        return {
            "player1_id": player1_id,
            "player2_id": player2_id,
            "player1_wins": player1_wins,
            "player2_wins": player2_wins,
            "total_matches": matches.count(),
            "matches": list(
                matches.values(
                    "id",
                    "tournament__name",
                    "round",
                    "winner_id",
                    "scheduled_time",
                    "created_at",
                )
            ),
        }
