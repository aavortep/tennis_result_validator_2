from .user_dto import UserDTO

def to_user_dto(user):
    return UserDTO(
        user.id,
        user.username,
        user.first_name,
        user.last_name,
        user.email,
        user.role,
        user.phone,
        user.bio
    )
