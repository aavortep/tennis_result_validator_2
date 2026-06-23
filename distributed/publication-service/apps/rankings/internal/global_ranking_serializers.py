from rest_framework import serializers

from shared.clients.user_service_client import UserServiceClient
from .global_ranking import GlobalRanking


class GlobalRankingSerializer(serializers.ModelSerializer):
    player = serializers.IntegerField(read_only=True)

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
    player_name = serializers.SerializerMethodField()

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
    
    def get_player_name(self, obj):
        player = UserServiceClient.get_user(obj.player)
        return player.username
