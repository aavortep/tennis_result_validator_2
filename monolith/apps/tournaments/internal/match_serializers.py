from rest_framework import serializers

from apps.users.web.public_serializers import UserPublicSerializer
from .match import Match

class MatchSerializer(serializers.ModelSerializer):
    player1 = UserPublicSerializer(read_only=True)
    player2 = UserPublicSerializer(read_only=True)
    referee = UserPublicSerializer(read_only=True)
    winner = UserPublicSerializer(read_only=True)
    tournament_name = serializers.CharField(source="tournament.name", read_only=True)

    class Meta:
        model = Match
        fields = [
            "id",
            "tournament",
            "tournament_name",
            "player1",
            "player2",
            "referee",
            "scheduled_time",
            "court",
            "round",
            "status",
            "winner",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class MatchCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = [
            "tournament",
            "player1",
            "player2",
            "referee",
            "scheduled_time",
            "court",
            "round",
        ]


class MatchListSerializer(serializers.ModelSerializer):
    player1_name = serializers.CharField(source="player1.username", read_only=True)
    player2_name = serializers.CharField(source="player2.username", read_only=True)
    tournament_name = serializers.CharField(source="tournament.name", read_only=True)

    class Meta:
        model = Match
        fields = [
            "id",
            "tournament_name",
            "player1_name",
            "player2_name",
            "scheduled_time",
            "court",
            "round",
            "status",
        ]
