import requests
from ..dto.user_dto import UserDTO


class UserServiceClient:

    BASE_URL = "http://user-service:8000"

    @classmethod
    def get_user(cls, user_id: int):
        response = requests.get(
            f"{cls.BASE_URL}/api/accounts/users/{user_id}"
        )

        response.raise_for_status()
        data = response.json()

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