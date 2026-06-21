from rest_framework import serializers

from apps.users.web.public_serializers import UserPublicSerializer

from .ranking import Ranking


class RankingSerializer(serializers.ModelSerializer):
    player = UserPublicSerializer(read_only=True)
    tournament_name = serializers.CharField(source="tournament.name", read_only=True)
    matches_played = serializers.ReadOnlyField()
    win_percentage = serializers.ReadOnlyField()

    class Meta:
        model = Ranking
        fields = [
            "id",
            "player",
            "tournament",
            "tournament_name",
            "position",
            "points",
            "wins",
            "losses",
            "matches_played",
            "win_percentage",
            "sets_won",
            "sets_lost",
            "games_won",
            "games_lost",
            "created_at",
            "updated_at",
        ]


class RankingListSerializer(serializers.ModelSerializer):
    player_name = serializers.CharField(source="player.username", read_only=True)
    matches_played = serializers.ReadOnlyField()

    class Meta:
        model = Ranking
        fields = [
            "id",
            "player_name",
            "position",
            "points",
            "wins",
            "losses",
            "matches_played",
        ]
