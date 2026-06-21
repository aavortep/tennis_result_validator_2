"""
Tests for validation services.
"""

from datetime import date, timedelta

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.internal.user import User
from apps.users.web.roles import Role
from apps.validation.internal.dispute import Dispute
from apps.validation.dispute_service import DisputeService
from apps.tournaments.internal.match import Match
from apps.tournaments.internal.tournament import Tournament
from shared.exceptions import (
    DisputeError,
    PermissionDeniedError,
)


class DisputeServiceTest(TestCase):
    """Test cases for DisputeService."""

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
            status=Match.Status.COMPLETED,
        )

    def test_create_dispute(self):
        """Test creating a dispute."""
        dispute = DisputeService.create_dispute(
            self.match.id, "Score was recorded incorrectly", self.player1
        )

        self.assertEqual(dispute.match, self.match)
        self.assertEqual(dispute.raised_by, self.player1)
        self.assertEqual(dispute.status, Dispute.Status.OPEN)
        self.match.refresh_from_db()
        self.assertEqual(self.match.status, Match.Status.DISPUTED)

    def test_create_duplicate_dispute_fails(self):
        """Test creating duplicate dispute fails."""
        DisputeService.create_dispute(self.match.id, "First dispute", self.player1)

        with self.assertRaises(DisputeError):
            DisputeService.create_dispute(self.match.id, "Second dispute", self.player2)

    def test_add_evidence(self):
        """Test adding evidence to dispute."""
        dispute = DisputeService.create_dispute(
            self.match.id, "Score dispute", self.player1
        )

        evidence = DisputeService.add_evidence(
            dispute.id, None, "Photo shows final score", self.player1
        )

        self.assertEqual(evidence.dispute, dispute)
        self.assertEqual(evidence.submitted_by, self.player1)

    def test_resolve_dispute(self):
        """Test resolving a dispute."""
        dispute = DisputeService.create_dispute(
            self.match.id, "Score dispute", self.player1
        )

        resolved = DisputeService.resolve_dispute(
            dispute.id,
            "After review, player1 wins",
            self.referee,
            winner_id=self.player1.id,
        )

        self.assertEqual(resolved.status, Dispute.Status.RESOLVED)
        self.assertEqual(resolved.resolved_by, self.referee)
        self.match.refresh_from_db()
        self.assertEqual(self.match.status, Match.Status.COMPLETED)
        self.assertEqual(self.match.winner, self.player1)

    def test_resolve_dispute_non_referee_fails(self):
        """Test resolving dispute by non-referee fails."""
        dispute = DisputeService.create_dispute(
            self.match.id, "Score dispute", self.player1
        )

        with self.assertRaises(PermissionDeniedError):
            DisputeService.resolve_dispute(dispute.id, "My resolution", self.player2)

    def test_mark_under_review(self):
        """Test marking dispute as under review."""
        dispute = DisputeService.create_dispute(
            self.match.id, "Score dispute", self.player1
        )

        reviewed = DisputeService.mark_under_review(dispute.id, self.referee)

        self.assertEqual(reviewed.status, Dispute.Status.UNDER_REVIEW)



class DisputeResolutionWorkflowTest(TestCase):
    """Integration tests for dispute resolution workflow."""

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
            status=Match.Status.COMPLETED,
        )

    def test_complete_dispute_workflow(self):
        """Test complete workflow: dispute creation, evidence, resolution."""
        # Step 1: Player creates dispute
        self.client.force_authenticate(user=self.player1)
        response = self.client.post(
            "/api/validation/disputes/create/",
            {
                "match": self.match.id,
                "reason": "Score was recorded incorrectly. I won 6-4, 6-3.",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        dispute_id = response.data["id"]

        # Verify match is now disputed
        self.match.refresh_from_db()
        self.assertEqual(self.match.status, Match.Status.DISPUTED)

        # Step 2: Player adds evidence
        response = self.client.post(
            "/api/validation/evidence/submit/",
            {
                "dispute": dispute_id,
                "description": "Screenshot of scoreboard showing final score",
            },
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Step 3: Other player adds counter-evidence
        self.client.force_authenticate(user=self.player2)
        response = self.client.post(
            "/api/validation/evidence/submit/",
            {"dispute": dispute_id, "description": "My video shows different score"},
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Step 4: Referee marks as under review
        self.client.force_authenticate(user=self.referee)
        response = self.client.post(f"/api/validation/disputes/{dispute_id}/review/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        dispute = Dispute.objects.get(id=dispute_id)
        self.assertEqual(dispute.status, Dispute.Status.UNDER_REVIEW)

        # Step 5: Referee resolves dispute
        response = self.client.post(
            f"/api/validation/disputes/{dispute_id}/resolve/",
            {
                "resolution_notes": "After reviewing evidence, player1 wins.",
                "winner_id": self.player1.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify resolution
        dispute.refresh_from_db()
        self.match.refresh_from_db()
        self.assertEqual(dispute.status, Dispute.Status.RESOLVED)
        self.assertEqual(dispute.resolved_by, self.referee)
        self.assertEqual(self.match.status, Match.Status.COMPLETED)
        self.assertEqual(self.match.winner, self.player1)


class RoleBasedAccessControlTest(TestCase):
    """Integration tests for role-based access control."""

    def setUp(self):
        self.client = APIClient()
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
        self.spectator = User.objects.create_user(
            username="spectator",
            email="spec@example.com",
            password="pass123",
            role=Role.SPECTATOR,
        )

    def test_only_organizer_can_create_tournament(self):
        """Test only organizers can create tournaments."""
        tournament_data = {
            "name": "Test Tournament",
            "start_date": str(date.today()),
            "end_date": str(date.today() + timedelta(days=7)),
            "location": "Test City",
        }

        # Organizer can create
        self.client.force_authenticate(user=self.organizer)
        response = self.client.post("/api/tournaments/", tournament_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Player cannot create
        self.client.force_authenticate(user=self.player)
        response = self.client.post("/api/tournaments/", tournament_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Spectator cannot create
        self.client.force_authenticate(user=self.spectator)
        response = self.client.post("/api/tournaments/", tournament_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_all_users_can_view_tournaments(self):
        """Test all authenticated users can view tournaments."""
        Tournament.objects.create(
            name="Test Tournament",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
            location="Test City",
            status=Tournament.Status.REGISTRATION,
            created_by=self.organizer,
        )

        for user in [self.organizer, self.player, self.spectator]:
            self.client.force_authenticate(user=user)
            response = self.client.get("/api/tournaments/")
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_cannot_access_protected_endpoints(self):
        """Test unauthenticated users cannot access protected endpoints."""
        response = self.client.post("/api/scores/submit/", {}, format="json")
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

        response = self.client.post("/api/tournaments/", {}, format="json")
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

