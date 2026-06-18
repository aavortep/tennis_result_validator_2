from dataclasses import dataclass


@dataclass
class UserDTO:
    id: int
    username: str
    first_name: str
    last_name: str
    email: str
    role: str
    phone: str
    bio: str
