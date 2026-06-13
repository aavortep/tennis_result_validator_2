"""
Tests for accounts services.
"""

from django.test import RequestFactory, TestCase

from apps.users.internal.user import User
from apps.users.internal.user_service_impl import UserServiceImpl
from shared.exceptions import PermissionDeniedError, ValidationError


class UserServiceTest(TestCase):
    """Test cases for UserService."""

    def setUp(self):
        self.factory = RequestFactory()

    def test_register_user(self):
        """Test user registration."""
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "securepass123",
            "first_name": "New",
            "last_name": "User",
            "role": User.Role.PLAYER,
        }
        user = UserServiceImpl.register_user(data)

        self.assertEqual(user.username, "newuser")
        self.assertEqual(user.email, "new@example.com")
        self.assertEqual(user.role, User.Role.PLAYER)
        self.assertTrue(user.check_password("securepass123"))

    def test_register_duplicate_username(self):
        """Test registration fails with duplicate username."""
        User.objects.create_user(
            username="existinguser", email="existing@example.com", password="pass123"
        )

        data = {
            "username": "existinguser",
            "email": "new@example.com",
            "password": "securepass123",
        }

        with self.assertRaises(ValidationError):
            UserServiceImpl.register_user(data)

    def test_register_duplicate_email(self):
        """Test registration fails with duplicate email."""
        User.objects.create_user(
            username="user1", email="same@example.com", password="pass123"
        )

        data = {
            "username": "user2",
            "email": "same@example.com",
            "password": "securepass123",
        }

        with self.assertRaises(ValidationError):
            UserServiceImpl.register_user(data)

    def test_update_profile(self):
        """Test profile update."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )

        updated = UserServiceImpl.update_profile(
            user,
            {
                "first_name": "Updated",
                "last_name": "Name",
                "phone": "1234567890",
            },
        )

        self.assertEqual(updated.first_name, "Updated")
        self.assertEqual(updated.last_name, "Name")
        self.assertEqual(updated.phone, "1234567890")

    def test_change_password(self):
        """Test password change."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="oldpass123"
        )

        UserServiceImpl.change_password(user, "oldpass123", "newpass456")
        user.refresh_from_db()

        self.assertTrue(user.check_password("newpass456"))
        self.assertFalse(user.check_password("oldpass123"))

    def test_change_password_wrong_old(self):
        """Test password change fails with wrong old password."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="oldpass123"
        )

        with self.assertRaises(ValidationError):
            UserServiceImpl.change_password(user, "wrongpass", "newpass456")

    def test_delete_own_account(self):
        """Test deleting own account."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        user_id = user.id

        UserServiceImpl.delete_account(user, user)

        self.assertFalse(User.objects.filter(id=user_id).exists())

    def test_delete_other_account_as_organizer(self):
        """Test organizer can delete other accounts."""
        organizer = User.objects.create_user(
            username="organizer",
            email="org@example.com",
            password="pass123",
            role=User.Role.ORGANIZER,
        )
        player = User.objects.create_user(
            username="player",
            email="player@example.com",
            password="pass123",
            role=User.Role.PLAYER,
        )
        player_id = player.id

        UserServiceImpl.delete_account(player, organizer)

        self.assertFalse(User.objects.filter(id=player_id).exists())

    def test_delete_other_account_denied(self):
        """Test non-organizer cannot delete other accounts."""
        player1 = User.objects.create_user(
            username="player1",
            email="p1@example.com",
            password="pass123",
            role=User.Role.PLAYER,
        )
        player2 = User.objects.create_user(
            username="player2",
            email="p2@example.com",
            password="pass123",
            role=User.Role.PLAYER,
        )

        with self.assertRaises(PermissionDeniedError):
            UserServiceImpl.delete_account(player1, player2)

    def test_get_all_players(self):
        """Test getting all players."""
        User.objects.create_user(
            username="player1",
            email="p1@example.com",
            password="pass",
            role=User.Role.PLAYER,
        )
        User.objects.create_user(
            username="player2",
            email="p2@example.com",
            password="pass",
            role=User.Role.PLAYER,
        )
        User.objects.create_user(
            username="referee",
            email="ref@example.com",
            password="pass",
            role=User.Role.REFEREE,
        )

        players = UserServiceImpl.get_all_players()

        self.assertEqual(len(players), 2)
        for player in players:
            self.assertEqual(player.role, User.Role.PLAYER)

    def test_get_all_referees(self):
        """Test getting all referees."""
        User.objects.create_user(
            username="ref1",
            email="r1@example.com",
            password="pass",
            role=User.Role.REFEREE,
        )
        User.objects.create_user(
            username="ref2",
            email="r2@example.com",
            password="pass",
            role=User.Role.REFEREE,
        )

        referees = UserServiceImpl.get_all_referees()

        self.assertEqual(len(referees), 2)
        for ref in referees:
            self.assertEqual(ref.role, User.Role.REFEREE)
