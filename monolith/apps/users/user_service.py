from abc import ABC, abstractmethod


class UserService(ABC):
    @abstractmethod
    def register_user(data):
        pass

    @abstractmethod
    def login_user(request, user):
        pass

    @abstractmethod
    def logout_user(request):
        pass

    @abstractmethod
    def update_profile(user, data):
        pass

    @abstractmethod
    def change_password(user, old_password, new_password):
        pass

    @abstractmethod
    def delete_account(user, requesting_user):
        pass

    @abstractmethod
    def get_all_users():
        pass

    @abstractmethod
    def get_users_by_role(role):
        pass

    @abstractmethod
    def get_all_players():
        pass

    @abstractmethod
    def get_all_referees():
        pass
