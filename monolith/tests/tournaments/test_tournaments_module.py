"""
Tests for tournament services.
"""

from datetime import date, timedelta

from django.test import TestCase

from apps.users.internal.user import User
from apps.users.web.roles import Role
from apps.tournaments.internal.match import Match
from apps.tournaments.internal.tournament import Tournament
from apps.tournaments.match_service import MatchService
from apps.tournaments.tournament_service import TournamentService
from shared.exceptions import (
    PermissionDeniedError,
    ValidationError,
)


class TournamentServiceTest(TestCase):
    """Test cases for TournamentService."""

    def setUp(self):
        self.organizer = User.objects.create_user(
            username="organizer",
            email="org@example.com",
            password="pass123",
            role=Role.ORGANIZER,
        )
        self.player = User.objects.create_user(
            username="player",
            email="player@example.com",
            password="pass123",
            role=Role.PLAYER,
        )
        self.referee = User.objects.create_user(
            username="referee",
            email="ref@example.com",
            password="pass123",
            role=Role.REFEREE,
        )

    def test_create_tournament(self):
        """Test tournament creation."""
        data = {
            "name": "New Tournament",
            "description": "Test description",
            "start_date": date.today(),
            "end_date": date.today() + timedelta(days=7),
            "location": "Test City",
            "max_players": 16,
        }

        tournament = TournamentService.create_tournament(data, self.organizer)

        self.assertEqual(tournament.name, "New Tournament")
        self.assertEqual(tournament.created_by, self.organizer)
        self.assertEqual(tournament.status, Tournament.Status.DRAFT)

    def test_create_tournament_non_organizer(self):
        """Test tournament creation fails for non-organizers."""
        data = {
            "name": "New Tournament",
            "start_date": date.today(),
            "end_date": date.today() + timedelta(days=7),
            "location": "Test City",
        }

        with self.assertRaises(PermissionDeniedError):
            TournamentService.create_tournament(data, self.player)

    def test_add_player(self):
        """Test adding player to tournament."""
        tournament = Tournament.objects.create(
            name="Test Tournament",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
            location="Test City",
            status=Tournament.Status.REGISTRATION,
            created_by=self.organizer,
        )

        TournamentService.add_player(tournament, self.player.id, self.organizer)

        self.assertIn(self.player, tournament.players.all())

    def test_add_player_tournament_full(self):
        """Test adding player fails when tournament is full."""
        tournament = Tournament.objects.create(
            name="Test Tournament",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
            location="Test City",
            status=Tournament.Status.REGISTRATION,
            max_players=1,
            created_by=self.organizer,
        )

        player1 = User.objects.create_user(
            username="p1", email="p1@test.com", password="pass", role=Role.PLAYER
        )
        player2 = User.objects.create_user(
            username="p2", email="p2@test.com", password="pass", role=Role.PLAYER
        )

        TournamentService.add_player(tournament, player1.id, self.organizer)

        with self.assertRaises(ValidationError):
            TournamentService.add_player(tournament, player2.id, self.organizer)

    def test_add_referee(self):
        """Test adding referee to tournament."""
        tournament = Tournament.objects.create(
            name="Test Tournament",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
            location="Test City",
            created_by=self.organizer,
        )

        TournamentService.add_referee(tournament, self.referee.id, self.organizer)

        self.assertIn(self.referee, tournament.referees.all())

    def test_open_registration(self):
        """Test opening tournament registration."""
        tournament = Tournament.objects.create(
            name="Test Tournament",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
            location="Test City",
            status=Tournament.Status.DRAFT,
            created_by=self.organizer,
        )

        TournamentService.open_registration(tournament, self.organizer)

        tournament.refresh_from_db()
        self.assertEqual(tournament.status, Tournament.Status.REGISTRATION)

    def test_start_tournament(self):
        """Test starting a tournament."""
        tournament = Tournament.objects.create(
            name="Test Tournament",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
            location="Test City",
            status=Tournament.Status.REGISTRATION,
            created_by=self.organizer,
        )
        player1 = User.objects.create_user(
            username="p1", email="p1@test.com", password="pass", role=Role.PLAYER
        )
        player2 = User.objects.create_user(
            username="p2", email="p2@test.com", password="pass", role=Role.PLAYER
        )
        tournament.players.add(player1, player2)

        TournamentService.start_tournament(tournament, self.organizer)

        tournament.refresh_from_db()
        self.assertEqual(tournament.status, Tournament.Status.IN_PROGRESS)

    def test_start_tournament_insufficient_players(self):
        """Test starting tournament fails with insufficient players."""
        tournament = Tournament.objects.create(
            name="Test Tournament",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
            location="Test City",
            status=Tournament.Status.REGISTRATION,
            created_by=self.organizer,
        )
        player1 = User.objects.create_user(
            username="p1", email="p1@test.com", password="pass", role=Role.PLAYER
        )
        tournament.players.add(player1)

        with self.assertRaises(ValidationError):
            TournamentService.start_tournament(tournament, self.organizer)


class MatchServiceTest(TestCase):
    """Test cases for MatchService."""

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
        self.referee = User.objects.create_user(
            username="referee",
            email="ref@example.com",
            password="pass123",
            role=Role.REFEREE,
        )
        self.tournament = Tournament.objects.create(
            name="Test Tournament",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
            location="Test City",
            status=Tournament.Status.IN_PROGRESS,
            created_by=self.organizer,
        )
        self.tournament.players.add(self.player1, self.player2)

    def test_create_match(self):
        """Test match creation."""
        data = {
            "tournament": self.tournament,
            "player1": self.player1,
            "player2": self.player2,
            "round": Match.Round.QUARTERFINAL,
        }

        match = MatchService.create_match(data, self.organizer)

        self.assertEqual(match.tournament, self.tournament)
        self.assertEqual(match.status, Match.Status.SCHEDULED)

    def test_assign_players(self):
        """Test assigning players to match."""
        match = Match.objects.create(
            tournament=self.tournament, round=Match.Round.SEMIFINAL
        )

        MatchService.assign_players(
            match, self.player1.id, self.player2.id, self.organizer
        )

        match.refresh_from_db()
        self.assertEqual(match.player1, self.player1)
        self.assertEqual(match.player2, self.player2)

    def test_assign_referee(self):
        """Test assigning referee to match."""
        match = Match.objects.create(
            tournament=self.tournament, player1=self.player1, player2=self.player2
        )

        MatchService.assign_referee(match, self.referee.id, self.organizer)

        match.refresh_from_db()
        self.assertEqual(match.referee, self.referee)

    def test_start_match(self):
        """Test starting a match."""
        match = Match.objects.create(
            tournament=self.tournament,
            player1=self.player1,
            player2=self.player2,
            referee=self.referee,
        )

        MatchService.start_match(match, self.organizer)

        match.refresh_from_db()
        self.assertEqual(match.status, Match.Status.IN_PROGRESS)

    def test_start_match_without_players(self):
        """Test starting match fails without players."""
        match = Match.objects.create(tournament=self.tournament, player1=self.player1)

        with self.assertRaises(ValidationError):
            MatchService.start_match(match, self.organizer)
