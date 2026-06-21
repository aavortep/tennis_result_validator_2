from rest_framework import serializers

from apps.users.web.public_serializers import UserPublicSerializer

from .global_ranking import GlobalRanking


class GlobalRankingSerializer(serializers.ModelSerializer):
    player = UserPublicSerializer(read_only=True)

    class Meta:
        model = GlobalRanking
        fields = [
            "id",
            "player",
            "position",
            "total_points",
            "total_wins",
            "total_losses",
            "tournaments_played",
            "tournaments_won",
            "updated_at",
        ]


class GlobalRankingListSerializer(serializers.ModelSerializer):
    player_name = serializers.CharField(source="player.username", read_only=True)

    class Meta:
        model = GlobalRanking
        fields = [
            "id",
            "player_name",
            "position",
            "total_points",
            "total_wins",
            "total_losses",
            "tournaments_played",
        ]
