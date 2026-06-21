import requests
from ..dto.user_dto import UserDTO


class UserServiceClient:

    BASE_URL = "http://users-service:8000"

    def json_to_user_dto(data):
        return UserDTO(
            id=data["id"],
            username=data["username"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            role=data["role"],
            phone=data["phone"],
            bio=data["bio"]
        )

    @classmethod
    def get_user(cls, user_id: int):
        response = requests.get(
            f"{cls.BASE_URL}/api/accounts/users/{user_id}"
        )

        response.raise_for_status()
        data = response.json()

        return cls.json_to_user_dto(data)
    
    @classmethod
    def get_all_players(cls):
        response = requests.get(
            f"{cls.BASE_URL}/api/accounts/players"
        )

        response.raise_for_status()
        data = response.json()

        return [cls.json_to_user_dto(player) for player in data]
    
    @classmethod
    def get_all_referees(cls):
        response = requests.get(
            f"{cls.BASE_URL}/api/accounts/referees"
        )

        response.raise_for_status()
        data = response.json()

        return [cls.json_to_user_dto(referee) for referee in data]
