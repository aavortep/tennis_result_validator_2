"""
Tests for results services.
"""

from datetime import date, timedelta

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.internal.user import User
from apps.users.web.roles import Role
from apps.results.internal.score import Score
from apps.results.score_service import ScoreService
from apps.tournaments.internal.match import Match
from apps.tournaments.internal.tournament import Tournament
from shared.exceptions import (
    InvalidStateError,
    PermissionDeniedError,
    ValidationError,
)


class ScoreServiceTest(TestCase):
    """Test cases for ScoreService."""

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
        self.match = Match.objects.create(
            tournament=self.tournament,
            player1=self.player1,
            player2=self.player2,
            referee=self.referee,
            status=Match.Status.IN_PROGRESS,
        )

    def test_submit_score_by_player(self):
        """Test player submitting score."""
        set_scores = [
            {"player1": 6, "player2": 4},
            {"player1": 6, "player2": 3},
        ]

        score = ScoreService.submit_score(self.match.id, set_scores, self.player1)

        self.assertEqual(score.match, self.match)
        self.assertEqual(score.submitted_by, self.player1)
        self.assertEqual(score.winner, self.player1)
        self.assertFalse(score.is_confirmed)

    def test_submit_score_by_referee(self):
        """Test referee submitting score (auto-confirmed)."""
        set_scores = [
            {"player1": 6, "player2": 4},
            {"player1": 6, "player2": 3},
        ]

        score = ScoreService.submit_score(self.match.id, set_scores, self.referee)

        self.assertTrue(score.is_confirmed)
        self.match.refresh_from_db()
        self.assertEqual(self.match.status, Match.Status.COMPLETED)

    def test_submit_score_invalid_user(self):
        """Test score submission by non-participant fails."""
        other_player = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="pass",
            role=Role.PLAYER,
        )
        set_scores = [{"player1": 6, "player2": 4}, {"player1": 6, "player2": 3}]

        with self.assertRaises(PermissionDeniedError):
            ScoreService.submit_score(self.match.id, set_scores, other_player)

    def test_submit_score_invalid_scores(self):
        """Test invalid score format."""
        set_scores = [{"player1": 5, "player2": 4}]  # Invalid - no winner

        with self.assertRaises(ValidationError):
            ScoreService.submit_score(self.match.id, set_scores, self.player1)

    def test_confirm_score(self):
        """Test confirming opponent's score."""
        set_scores = [
            {"player1": 6, "player2": 4},
            {"player1": 6, "player2": 3},
        ]
        score = ScoreService.submit_score(self.match.id, set_scores, self.player1)

        confirmed = ScoreService.confirm_score(score.id, self.player2)

        self.assertTrue(confirmed.is_confirmed)
        self.assertEqual(confirmed.confirmed_by, self.player2)
        self.match.refresh_from_db()
        self.assertEqual(self.match.status, Match.Status.COMPLETED)

    def test_confirm_own_score_fails(self):
        """Test confirming own score fails."""
        set_scores = [
            {"player1": 6, "player2": 4},
            {"player1": 6, "player2": 3},
        ]
        score = ScoreService.submit_score(self.match.id, set_scores, self.player1)

        with self.assertRaises(ValidationError):
            ScoreService.confirm_score(score.id, self.player1)

    def test_update_score(self):
        """Test updating score."""
        set_scores = [
            {"player1": 6, "player2": 4},
            {"player1": 6, "player2": 3},
        ]
        score = ScoreService.submit_score(self.match.id, set_scores, self.player1)

        new_scores = [
            {"player1": 6, "player2": 4},
            {"player1": 7, "player2": 5},
        ]
        updated = ScoreService.update_score(score.id, new_scores, self.player1)

        self.assertEqual(updated.set_scores, new_scores)

    def test_update_confirmed_score_fails(self):
        """Test updating confirmed score fails."""
        set_scores = [
            {"player1": 6, "player2": 4},
            {"player1": 6, "player2": 3},
        ]
        score = ScoreService.submit_score(self.match.id, set_scores, self.referee)

        new_scores = [{"player1": 7, "player2": 5}, {"player1": 6, "player2": 4}]

        with self.assertRaises(InvalidStateError):
            ScoreService.update_score(score.id, new_scores, self.referee)

    def test_delete_score(self):
        """Test deleting score."""
        set_scores = [
            {"player1": 6, "player2": 4},
            {"player1": 6, "player2": 3},
        ]
        score = ScoreService.submit_score(self.match.id, set_scores, self.player1)
        score_id = score.id

        ScoreService.delete_score(score_id, self.player1)

        self.assertFalse(Score.objects.filter(id=score_id).exists())


class ScoreSubmissionWorkflowTest(TestCase):
    """Integration tests for complete score submission workflow."""

    def setUp(self):
        self.client = APIClient()
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
        self.match = Match.objects.create(
            tournament=self.tournament,
            player1=self.player1,
            player2=self.player2,
            referee=self.referee,
            status=Match.Status.IN_PROGRESS,
        )

    def test_complete_score_workflow_player_submission(self):
        """Test complete workflow: player submits, opponent confirms."""
        # Step 1: Player 1 submits score
        self.client.force_authenticate(user=self.player1)
        response = self.client.post(
            "/api/scores/submit/",
            {
                "match": self.match.id,
                "set_scores": [
                    {"player1": 6, "player2": 4},
                    {"player1": 6, "player2": 3},
                ],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        score_id = response.data["id"]

        # Verify score is unconfirmed
        score = Score.objects.get(id=score_id)
        self.assertFalse(score.is_confirmed)
        self.assertEqual(score.winner, self.player1)

        # Step 2: Player 2 confirms score
        self.client.force_authenticate(user=self.player2)
        response = self.client.post(f"/api/scores/{score_id}/confirm/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify score is confirmed and match completed
        score.refresh_from_db()
        self.match.refresh_from_db()
        self.assertTrue(score.is_confirmed)
        self.assertEqual(score.confirmed_by, self.player2)
        self.assertEqual(self.match.status, Match.Status.COMPLETED)
        self.assertEqual(self.match.winner, self.player1)

    def test_referee_score_auto_confirms(self):
        """Test referee score submission auto-confirms."""
        self.client.force_authenticate(user=self.referee)
        response = self.client.post(
            "/api/scores/submit/",
            {
                "match": self.match.id,
                "set_scores": [
                    {"player1": 6, "player2": 4},
                    {"player1": 3, "player2": 6},
                    {"player1": 6, "player2": 2},
                ],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        score = Score.objects.get(id=response.data["id"])
        self.assertTrue(score.is_confirmed)
        self.match.refresh_from_db()
        self.assertEqual(self.match.status, Match.Status.COMPLETED)
