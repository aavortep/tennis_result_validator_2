"""
Tests for ranking services.
"""

from datetime import date, timedelta

from django.test import TestCase

from apps.users.internal.user import User
from apps.users.web.roles import Role
from apps.publication.internal.ranking import Ranking
from apps.publication.internal.global_ranking import GlobalRanking
from apps.publication.ranking_service import RankingService
from apps.tournaments.internal.match import Match
from apps.tournaments.internal.tournament import Tournament


class RankingServiceTest(TestCase):
    """Test cases for RankingService."""

    def setUp(self):
        self.organizer = User.objects.create_user(
            username="organizer",
            email="org@example.com",
            password="pass123",
            role=Role.ORGANIZER,
        )
        self.player1 = User.objects.create_user(
            username="player1",
            email="p1@example.com",
            password="pass123",
            role=Role.PLAYER,
        )
        self.player2 = User.objects.create_user(
            username="player2",
            email="p2@example.com",
            password="pass123",
            role=Role.PLAYER,
        )
        self.player3 = User.objects.create_user(
            username="player3",
            email="p3@example.com",
            password="pass123",
            role=Role.PLAYER,
        )
        self.tournament = Tournament.objects.create(
            name="Test Tournament",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
            location="Test City",
            status=Tournament.Status.IN_PROGRESS,
            created_by=self.organizer,
        )
        self.tournament.players.add(self.player1, self.player2, self.player3)

    def test_initialize_tournament_rankings(self):
        """Test initializing rankings for tournament."""
        RankingService.initialize_tournament_rankings(self.tournament)

        rankings = Ranking.objects.filter(tournament=self.tournament)
        self.assertEqual(rankings.count(), 3)

    def test_update_ranking_after_match(self):
        """Test updating rankings after match."""
        RankingService.initialize_tournament_rankings(self.tournament)

        match = Match.objects.create(
            tournament=self.tournament,
            player1=self.player1,
            player2=self.player2,
            status=Match.Status.COMPLETED,
            winner=self.player1,
            round=Match.Round.QUARTERFINAL,
        )

        RankingService.update_ranking_after_match(match)

        winner_ranking = Ranking.objects.get(
            player=self.player1, tournament=self.tournament
        )
        loser_ranking = Ranking.objects.get(
            player=self.player2, tournament=self.tournament
        )

        self.assertEqual(winner_ranking.wins, 1)
        self.assertEqual(loser_ranking.losses, 1)
        self.assertGreater(winner_ranking.points, loser_ranking.points)

    def test_recalculate_positions(self):
        """Test recalculating positions."""
        RankingService.initialize_tournament_rankings(self.tournament)

        # Set up different points
        r1 = Ranking.objects.get(player=self.player1, tournament=self.tournament)
        r2 = Ranking.objects.get(player=self.player2, tournament=self.tournament)
        r3 = Ranking.objects.get(player=self.player3, tournament=self.tournament)

        r1.points = 100
        r1.wins = 2
        r1.save()

        r2.points = 200
        r2.wins = 3
        r2.save()

        r3.points = 50
        r3.wins = 1
        r3.save()

        RankingService.recalculate_positions(self.tournament)

        r1.refresh_from_db()
        r2.refresh_from_db()
        r3.refresh_from_db()

        self.assertEqual(r2.position, 1)
        self.assertEqual(r1.position, 2)
        self.assertEqual(r3.position, 3)

    def test_update_global_ranking(self):
        """Test updating global ranking."""
        RankingService.initialize_tournament_rankings(self.tournament)

        ranking = Ranking.objects.get(player=self.player1, tournament=self.tournament)
        ranking.points = 500
        ranking.wins = 5
        ranking.losses = 1
        ranking.save()

        RankingService.update_global_ranking(self.player1)

        global_ranking = GlobalRanking.objects.get(player=self.player1)
        self.assertEqual(global_ranking.total_points, 500)
        self.assertEqual(global_ranking.total_wins, 5)
        self.assertEqual(global_ranking.total_losses, 1)

    def test_get_tournament_leaderboard(self):
        """Test getting tournament leaderboard."""
        RankingService.initialize_tournament_rankings(self.tournament)

        # Set positions
        for i, player in enumerate([self.player1, self.player2, self.player3], 1):
            r = Ranking.objects.get(player=player, tournament=self.tournament)
            r.position = i
            r.points = 100 * (4 - i)
            r.save()

        leaderboard = RankingService.get_tournament_leaderboard(self.tournament.id)

        self.assertEqual(leaderboard.count(), 3)
        self.assertEqual(leaderboard[0].player, self.player1)
        self.assertEqual(leaderboard[1].player, self.player2)
        self.assertEqual(leaderboard[2].player, self.player3)

    def test_get_player_rankings(self):
        """Test getting player rankings across tournaments."""
        tournament2 = Tournament.objects.create(
            name="Second Tournament",
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=37),
            location="Test City",
            created_by=self.organizer,
        )
        tournament2.players.add(self.player1)

        RankingService.initialize_tournament_rankings(self.tournament)
        RankingService.initialize_tournament_rankings(tournament2)

        player_rankings = RankingService.get_player_rankings(self.player1.id)

        self.assertEqual(player_rankings.count(), 2)

    def test_finalize_tournament_rankings(self):
        """Test finalizing tournament rankings."""
        RankingService.initialize_tournament_rankings(self.tournament)

        final_match = Match.objects.create(
            tournament=self.tournament,
            player1=self.player1,
            player2=self.player2,
            status=Match.Status.COMPLETED,
            winner=self.player1,
            round=Match.Round.FINAL,
        )

        RankingService.finalize_tournament_rankings(self.tournament)

        winner_ranking = Ranking.objects.get(
            player=self.player1, tournament=self.tournament
        )
        self.assertGreaterEqual(winner_ranking.points, RankingService.WINNER_BONUS)

    def test_head_to_head_stats(self):
        """Test getting head to head stats between players."""
        Match.objects.create(
            tournament=self.tournament,
            player1=self.player1,
            player2=self.player2,
            status=Match.Status.COMPLETED,
            winner=self.player1,
            round=Match.Round.QUARTERFINAL,
        )
        Match.objects.create(
            tournament=self.tournament,
            player1=self.player2,
            player2=self.player1,
            status=Match.Status.COMPLETED,
            winner=self.player1,
            round=Match.Round.SEMIFINAL,
        )
        Match.objects.create(
            tournament=self.tournament,
            player1=self.player1,
            player2=self.player2,
            status=Match.Status.COMPLETED,
            winner=self.player2,
            round=Match.Round.FINAL,
        )

        stats = RankingService.get_head_to_head(self.player1.id, self.player2.id)

        self.assertEqual(stats["total_matches"], 3)
        self.assertEqual(stats["player1_wins"], 2)
        self.assertEqual(stats["player2_wins"], 1)
        self.assertEqual(len(stats["matches"]), 3)
