from django.contrib.auth import login, logout
from shared.exceptions import PermissionDeniedError, ValidationError
from apps.users.user_service import UserService
from .user import User
from .helpers import to_user_dto


class UserServiceImpl(UserService):
    def register_user(data):
        if User.objects.filter(username=data["username"]).exists():
            raise ValidationError("Username already exists.")

        if User.objects.filter(email=data["email"]).exists():
            raise ValidationError("Email already exists.")

        user = User.objects.create_user(
            username=data["username"],
            email=data["email"],
            password=data["password"],
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            role=data.get("role", User.Role.SPECTATOR),
            phone=data.get("phone", ""),
            bio=data.get("bio", ""),
        )
        return user

    def login_user(request, user):
        login(request, user)

    def logout_user(request):
        logout(request)

    def update_profile(user, data):
        for field, value in data.items():
            if hasattr(user, field) and field not in (
                "password",
                "role",
                "is_staff",
                "is_superuser",
            ):
                setattr(user, field, value)
        user.save()
        return user

    def change_password(user, old_password, new_password):
        if not user.check_password(old_password):
            raise ValidationError("Current password is incorrect.")
        user.set_password(new_password)
        user.save()

    def delete_account(user, requesting_user):
        if user.id != requesting_user.id and not requesting_user.is_organizer:
            raise PermissionDeniedError("You can only delete your own account.")

        user.delete()

    def get_all_users():
        users = User.objects.filter(is_active=True)
        return [to_user_dto(user) for user in users]

    def get_user(user_id):
        try:
            user = User.objects.get(id=user_id, is_active=True)
            return to_user_dto(user)
        except User.DoesNotExist:
            return None

    def get_users_by_role(role):
        users = User.objects.filter(role=role, is_active=True)
        return [to_user_dto(user) for user in users]

    def get_all_players():
        users = User.objects.filter(role=User.Role.PLAYER, is_active=True)
        return [to_user_dto(user) for user in users]

    def get_player(player_id):
        try:
            user = User.objects.get(id=player_id, role=User.Role.PLAYER)
            return to_user_dto(user)
        except User.DoesNotExist:
            return None

    def get_all_referees():
        users = User.objects.filter(role=User.Role.REFEREE, is_active=True)
        return [to_user_dto(user) for user in users]
    
    def get_referee(referee_id):
        try:
            user = User.objects.get(id=referee_id, role=User.Role.REFEREE)
            return to_user_dto(user)
        except User.DoesNotExist:
            return None
